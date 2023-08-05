"""
Visualizes a completed pathogen build in Auspice, the Nextstrain visualization app.

The data directory should contain sets of Auspice JSON¹ files like

    <name>.json

or

    <name>_tree.json
    <name>_meta.json

The viewer runs inside a container, which requires Docker.  Run `nextstrain
check-setup` to check if Docker is installed and works.

¹ <https://nextstrain.github.io/auspice/introduction/how-to-run#input-file-formats>
"""

import re
import netifaces as net
from pathlib import Path
from typing import Iterable
from .. import runner
from ..argparse import add_extended_help_flags
from ..runner import docker, native
from ..util import colored, remove_suffix, warn
from ..volume import store_volume


def register_parser(subparser):
    """
    %(prog)s [options] <directory>
    %(prog)s --help
    """

    parser = subparser.add_parser("view", help = "View pathogen build", add_help = False)

    # Support --help and --help-all
    add_extended_help_flags(parser)

    parser.add_argument(
        "--allow-remote-access",
        help   = "Allow other computers on the network to access the website",
        action = "store_true")

    parser.add_argument(
        "--port",
        help    = "Listen on the given port instead of the default port %(default)s",
        metavar = "<number>",
        type    = int,
        default = 4000)

    # Positional parameters
    parser.add_argument(
        "directory",
        help    = "Path to directory containing JSONs for Auspice",
        metavar = "<directory>",
        action  = store_volume("auspice/data"))

    # Register runners; only Docker is supported for now.
    runner.register_runners(
        parser,
        exec    = ["auspice", "view", "--verbose", "--datasetDir=."],
        runners = [docker, native])

    return parser


def run(opts):
    # Ensure our data path is a directory that exists
    data_dir = opts.auspice_data.src

    if not data_dir.is_dir():
        warn("Error: Data path \"%s\" does not exist or is not a directory." % data_dir)

        if not data_dir.is_absolute():
            warn()
            warn("Perhaps your current working directory is different than you expect?")

        return 1

    # Find the available dataset paths
    datasets = dataset_paths(data_dir)

    # Setup the published port.  Default to localhost for security reasons
    # unless explicitly told otherwise.
    #
    # The environment variables HOST and PORT are respected by auspice's
    # cli/view.js.  HOST requires a new enough version of Auspice; 1.35.7 and
    # earlier always listen on 0.0.0.0 or ::.
    host = "0.0.0.0" if opts.allow_remote_access else "127.0.0.1"
    port = opts.port

    env = {
        'HOST': host,
        'PORT': str(port)
    }

    # These are docker-specific details which will only be used when the
    # docker runner (--docker flag) is in use.
    opts.docker_args = [
        *opts.docker_args,

        # auspice's cli (probably thanks to Express or Node?) when run in the
        # circumstances of the container seems to ignore signals (like SIGINT,
        # ^C, or SIGTERM), so run it under an init process that does respect
        # signals.
        "--init",

        # Inside the container, always bind to all interfaces.  This is
        # required for Docker to forward a port from the container's host into
        # the container because of how it does port publishing.  Note that
        # container ports aren't automatically published outside the container,
        # so this still doesn't allow arbitrary access from the outside world.
        # The published port on the container's host is still bound to
        # 127.0.0.1 by default.
        "--env=HOST=0.0.0.0",

        # Publish the port
        "--publish=%s:%d:%d" % (host, port, port),
    ]

    # Find the best remote address if we're allowing remote access.  While we
    # listen on all interfaces (0.0.0.0), only the local host can connect to
    # that successfully.  Remote hosts need a real IP on the network, which we
    # do our best to discover.  If something goes wrong, ignore it and leave
    # the host IP as-is (0.0.0.0); it'll at least work for local access.
    if opts.allow_remote_access:
        try:
            remote_address = best_remote_address()
        except:
            pass
        else:
            host = remote_address

    # Show a helpful message about where to connect
    print_url(host, port, datasets)

    return runner.run(opts, working_volume = opts.auspice_data, extra_env = env)


def dataset_paths(data_dir: Path) -> Iterable[str]:
    """
    Returns a :py:class:`set` of Auspice (not filesystem) paths for datasets in
    *data_dir*.
    """
    # v2: All *.json files which don't end with a known sidecar or v1 suffix.
    sidecar_suffixes = {"meta", "tree", "root-sequence", "seq", "sequences", "tip-frequencies", "entropy"}

    def sidecar_file(path):
        return any(path.name.endswith("_%s.json" % suffix) for suffix in sidecar_suffixes)

    datasets_v2 = set(
        path.stem.replace("_", "/")
            for path in data_dir.glob("*.json")
            if not sidecar_file(path))

    # v1: All *_tree.json files with corresponding *_meta.json files.
    def meta_exists(path):
        return path.with_name(remove_suffix("_tree.json", path.name) + "_meta.json").exists()

    datasets_v1 = set(
        re.sub(r"_tree$", "", path.stem).replace("_", "/")
            for path in data_dir.glob("*_tree.json")
            if meta_exists(path))

    return datasets_v2 | datasets_v1


def print_url(host, port, datasets):
    """
    Prints a list of available dataset URLs, if any.  Otherwise, prints a
    generic URL.
    """

    def url(path = None):
        return colored(
            "blue",
            "http://{host}:{port}/{path}".format(
                host = host,
                port = port,
                path = path if path is not None else ""))

    horizontal_rule = colored("green", "—" * 78)

    print()
    print(horizontal_rule)

    if len(datasets):
        print("    The following datasets should be available in a moment:")
        for path in sorted(datasets, key = str.casefold):
            print("       • %s" % url(path))
    else:
        print("    Open <%s> in your browser." % url())
        print()
        print("   ", colored("yellow", "Warning: No datasets detected."))

    print(horizontal_rule)
    print()


def best_remote_address():
    """
    Returns the "best" non-localback IP address for the local host, if
    possible.  The "best" IP address is that bound to either the default
    gateway interface, if any, else the arbitrary first interface found.

    IPv4 is preferred, but IPv6 will be used if no IPv4 interfaces/addresses
    are available.
    """
    default_gateway   = net.gateways().get("default", {})
    default_interface = default_gateway.get(net.AF_INET,  (None, None))[1] \
                     or default_gateway.get(net.AF_INET6, (None, None))[1] \
                     or net.interfaces()[0]

    interface_addresses = net.ifaddresses(default_interface).get(net.AF_INET)  \
                       or net.ifaddresses(default_interface).get(net.AF_INET6) \
                       or []

    addresses = [
        address["addr"]
            for address in interface_addresses
             if address.get("addr")
    ]

    return addresses[0] if addresses else None
