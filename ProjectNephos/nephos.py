#!/usr/bin/env python3

import argparse

from ProjectNephos.config import parse_config

ActionHandlers = []


def main():
    config = parse_config()

    # TODO: More information can be added to the definitions below
    parser = argparse.ArgumentParser(prog='nephos')
    parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Log a lot more things.',
    )

    subparser = parser.add_subparsers(dest='subc')
    for handler in ActionHandlers:
        handler._init_args(subparser)

    args = parser.parse_args()

    if args.subc is None:
        parser.print_help()
        exit(0)

    # This line basically selects the correct ActionHandler from the list and returns it.
    h = list(filter(lambda x: x.subcommand == args.subc, ActionHandlers))[0]
    h.run(args, config)


if __name__ == '__main__':
    main()
