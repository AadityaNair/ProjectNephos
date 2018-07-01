from ProjectNephos.backends import DriveStorage
from ProjectNephos.config import Configuration
from ProjectNephos.handlers.base import BaseHandler
from ProjectNephos.handlers.search import SearchHandler

from argparse import _SubParsersAction, Namespace
from logging import getLogger

logger = getLogger(__name__)


class TagHandler(BaseHandler):
    """
    This class is used to tag *uploaded* files. Tags currently are just strings
    that are added in the file's description field.
    These tags are of the form: "<tag>:<value>"

    This has two main drawbacks as of now,
        1. No control over the tag types. User can upload any data as tag.
        2. Updating tags is not implemented.

    NOTE: Mechanism to tag file while uploading has not yet been implemented.
    """

    def init_with_config(self, config: Configuration):
        super().init_with_config(config)

        self.backend = DriveStorage(config)
        self.search = SearchHandler(config=config)

    def init_args(self, subparser: _SubParsersAction) -> None:
        parser = super().init_args(subparser)

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

    def execute_command(self, fileId, tags):
        self.backend.tag(fileId, tags)

    def run(self, args: Namespace):
        logger.debug(args)

        relevant_files = self.search.execute_command(
            name=args.for_name, tags=None, do_and=False
        )

        filenames = [x[0] for x in relevant_files]
        logger.debug("The following files were found: {}".format(filenames))
        logger.debug(
            "The following tags are going to be added: {}".format(args.add_tags)
        )

        file_ids = [x[1] for x in relevant_files]

        for fid in file_ids:
            self.backend.tag(fid, args.add_tags)
