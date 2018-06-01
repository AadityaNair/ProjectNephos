from ProjectNephos.backends.GDrive import DriveStorage

from configparser import ConfigParser
from argparse import _SubParsersAction, Namespace
from logging import getLogger
from os import path

logger = getLogger(__name__)


class UploadHandler(object):

    def __init__(self, subcommand: str, config: ConfigParser):
        self.subcommand = subcommand
        self.backend = DriveStorage(config)

    def _init_args(self, subparser: _SubParsersAction) -> None:
        parser = subparser.add_parser(self.subcommand)
        parser.add_argument("files", nargs="+", help="Files you want to upload.")

    def run(self, args: Namespace):
        if not args.ignore_errors:
            bad_items = filter(lambda x: not path.isfile(x), args.files)
            if len(list(bad_items)) != 0:
                logger.critical(
                    "Operation aborted because some files did not exist."
                    "To upload other files, pass the --ignore_errors option."
                    "The following files were not found: {}".format(bad_items)
                )
                return None

        for f in args.files:
            if not path.isfile(f):
                logger.warning("{} is not a valid file. Ignoring.".format(f))
            self.backend.write(f)
