#!/usr/bin/env python3

import argparse
import logging

from ProjectNephos.config import Configuration, CONFIG_FULL_PATH_DEFAULT

from ProjectNephos.handlers.upload import UploadHandler
from ProjectNephos.handlers.search import SearchHandler
from ProjectNephos.handlers.tag import TagHandler
from ProjectNephos.handlers.process import ProcessHandler
from ProjectNephos.handlers.init import InitHandler
from ProjectNephos.handlers.permissions import PermissionHandler
from ProjectNephos.handlers.channels import ChannelHandler

ActionHandlers = [
    UploadHandler("upload"),
    SearchHandler("search"),
    TagHandler("tag"),
    ProcessHandler("process"),
    InitHandler("init"),
    PermissionHandler("permission"),
    ChannelHandler("channel"),
]


def main():

    # TODO: More information can be added to the definitions below
    parser = argparse.ArgumentParser(prog="nephos")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging. Beware, it prints a lot of things.",
    )
    parser.add_argument(
        "--ignore_errors",
        action="store_true",
        help="Ignore errors encountered in some operations and continue",
    )
    parser.add_argument(
        "--config",
        action="store",
        help="Specify the config file to read from. The default is ~/.nephos/config.ini."
        "The default will be created after running init",
        default=CONFIG_FULL_PATH_DEFAULT,
    )

    subparser = parser.add_subparsers(dest="subc")
    for handler in ActionHandlers:
        handler.init_args(subparser)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    if args.subc is None:
        parser.print_help()
        exit(0)

    # This line basically selects the correct ActionHandler from the list and returns it.
    h = list(filter(lambda x: x.subcommand == args.subc, ActionHandlers))[0]

    # We don't want to use config with init. That will actually create a new config or
    # folders from the specified config file
    if h.subcommand != "init":
        config = Configuration(args.config)
        h.init_with_config(config)
    h.run(args)


if __name__ == "__main__":
    main()
