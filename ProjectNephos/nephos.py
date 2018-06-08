#!/usr/bin/env python3

import argparse
import logging

from ProjectNephos.config import parse_config
from ProjectNephos.handlers.upload import UploadHandler
from ProjectNephos.handlers.search import SearchHandler
from ProjectNephos.handlers.tag import TagHandler

config = parse_config()
ActionHandlers = [
    UploadHandler("upload", config),
    SearchHandler("search", config),
    TagHandler("tag", config),
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

    subparser = parser.add_subparsers(dest="subc")
    for handler in ActionHandlers:
        handler._init_args(subparser)

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
    h.run(args)


if __name__ == "__main__":
    main()
