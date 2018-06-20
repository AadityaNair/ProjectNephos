from ProjectNephos.backends.GDrive import DriveStorage

from configparser import ConfigParser
from argparse import _SubParsersAction, Namespace
from logging import getLogger

logger = getLogger(__name__)


class SearchHandler(object):
    """
    This class does the searching. You provide it with search parameters and
    it find all matching files and their corresponding ids.

    This takes two search parameters: name and tags.
    *Name* is the actual filename it was uploaded with. Only one is allowed.
    *Tag* is the metadata the file was tagged with as defined in the TagHandler docs.
     There can be multiple tags supplied.

     Searching requires atleast one of them. If there are multiple tags or if both of
     them are supplied, the *do_and* parameter comes into play.
     If it is false, the search terms will be combined with an OR operator,
     i.e. "name OR tag1 OR tag2 ..."
     If true though, the ORs are replaced with ANDs, "name AND tag1 AND tag2 ..."

     More fine-grained controls will be added later.
    """

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

    def execute_command(self, name, tags, do_and):
        if not name and not tags:
            logger.critical(
                "Neither name or tags specified. Atleast one is required. Exiting"
            )
            return
        else:
            response = self.backend.search(name_subs=name, tag_subs=tags, do_and=do_and)
        return [(name, fid) for name, fid in response]

    def run(self, args: Namespace):
        logger.debug(args)
        if not args.name and not args.tags:
            logger.critical(
                "Neither name or tags specified. Atleast one is required. Exiting"
            )
            return
        else:
            response = self.execute_command(args.name, args.tags, args.do_and)

            #  TODO: Format Nicely
            print("Files\tIDs")
            for name, id in response:
                print("{}\t{}".format(name, id))
