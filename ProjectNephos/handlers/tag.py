from ProjectNephos.backends.GDrive import DriveStorage
from ProjectNephos.handlers.search import SearchHandler

from configparser import ConfigParser
from argparse import _SubParsersAction, Namespace
from logging import getLogger

logger = getLogger(__name__)


class TagHandler(object):

    def __init__(self, subcommand: str, config: ConfigParser):
        self.subcommand = subcommand
        self.backend = DriveStorage(config)
        self.search = SearchHandler("search", config)

    def _init_args(self, subparser: _SubParsersAction) -> None:
        parser = subparser.add_parser(self.subcommand)
        parser.add_argument(
            "--for_name",
            action="store",
            metavar="NAME",
            help="Search for items with NAME",
        )
        parser.add_argument(
            "--add_tags",
            action="store",
            nargs="+",
            help="add the provided tags to the search results",
        )

    def execute_command(self):
        pass

    def run(self, args: Namespace):
        logger.debug(args)

        relevant_files = self.search.execute_command(
            name=args.for_name, tags=None, do_and=False
        )

        filenames = [x[0] for x in relevant_files]
        logger.debug("The following files were found: {}".format(filenames))
        logger.debug("The following tags are going to be added: {}".format(args.add_tags))

        file_ids = [x[1] for x in relevant_files]

        for fid in file_ids:
            self.backend.tag(fid, args.add_tags)
