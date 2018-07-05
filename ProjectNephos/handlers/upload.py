from ProjectNephos.backends import DriveStorage
from ProjectNephos.config import Configuration
from ProjectNephos.handlers.base import BaseHandler

from argparse import _SubParsersAction, Namespace
from logging import getLogger
from os import path


logger = getLogger(__name__)


class UploadHandler(BaseHandler):
    """
    Upload files to google drive. Really, that's it. You supply it a file or
    a list of files and this will upload it for you. Raises errors on non-existant
    files based on the --ignore-errors argument.
    """

    def init_with_config(self, config):
        super().init_with_config(config)

        self.backend = DriveStorage(config)

    def init_args(self, subparser):
        parser = super().init_args(subparser)

        parser.add_argument("files", nargs="+", help="Files you want to upload.")

    def execute_command(self, filepath):
        return self.backend.write(filepath)

    def run(self, args):
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
