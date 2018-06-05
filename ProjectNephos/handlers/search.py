from ProjectNephos.backends.GDrive import DriveStorage

from configparser import ConfigParser
from argparse import _SubParsersAction, Namespace
from logging import getLogger

logger = getLogger(__name__)


class SearchHandler(object):

    def __init__(self, subcommand: str, config: ConfigParser):
        self.subcommand = subcommand
        self.backend = DriveStorage(config)

    def _init_args(self, subparser: _SubParsersAction) -> None:
        parser = subparser.add_parser(self.subcommand)
        parser.add_argument("--name", action="store", help="Search for a name")
        parser.add_argument(
            "--tags", action="store", nargs="*", help="Tags you want to search for"
        )
        parser.add_argument(
            "--do_and",
            action="store_true",
            help="Make sure all the tags are ANDed instead of ORed by default",
        )

    def run(self, args: Namespace):
        logger.debug(args)
        if not args.name and not args.tags:
            logger.critical(
                "Neither name or tags specified. Atleast one is required. Exiting"
            )
            return
        else:
            response = self.backend.search(
                name_subs=args.name, tag_subs=args.tags, do_and=args.do_and
            )

            #  TODO: Format Nicely
            print("Files\tIDs")
            for name, id in response:
                print("{}\t{}".format(name, id))
