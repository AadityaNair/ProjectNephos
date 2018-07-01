from ProjectNephos.backends import DriveStorage, DBStorage
from ProjectNephos.config import Configuration
from ProjectNephos.handlers.base import BaseHandler
from ProjectNephos.handlers.search import SearchHandler

from argparse import _SubParsersAction, Namespace
from logging import getLogger

logger = getLogger(__name__)


class PermissionHandler(BaseHandler):
    """
    This class handles adding permissions to uploaded files.

    This has two main drawbacks as of now,
        1. No control over the tag types. User can upload any data as tag.
        2. Updating tags is not implemented.

    NOTE: Mechanism to tag file while uploading has not yet been implemented.
    """

    def init_with_config(self, config: Configuration):
        super().init_with_config(config)

        self.backend = DriveStorage(config)
        self.db = DBStorage(config)
        self.search = SearchHandler(config=config)

    def init_args(self, subparser: _SubParsersAction) -> None:
        parser = super().init_args(subparser)

        parser.add_argument(
            "action", help="Define what action to take.", choices=["list", "add"]
        )
        parser.add_argument(
            "--for_tags", help="Define which tags to add permissions for ", nargs="+"
        )
        parser.add_argument(
            "--share_with", help="email id of the person to share with."
        )
        parser.add_argument(
            "--not_persistent",
            action="store_true",
            help="If provided, future uploads wont be shared.",
        )

    def execute_command(self):
        pass

    def run(self, args: Namespace):
        if args.action == "add":
            if not args.for_tags:
                logger.critical("--for_tags is required. Try again.")
            elif not args.share_with:
                logger.critical("--share_with is required. Try again.")
            else:
                tags = args.for_tags
                email = args.share_with
                role = "reader"

                if not args.not_persistent:
                    self.db.add_permissions(tags, email, role)
                response = self.search.execute_command(
                    name=None, tags=tags, do_and=False
                )

                for item in response:
                    id = item[1]
                    self.backend.add_permissions_user(fileid=id, email=email, role=role)

        if args.action == "list":
            if args.for_tags is None:
                print(self.db.get_all_permissions())
            else:
                for tag in args.for_tags:
                    print(self.db.get_permissions_from_tag(tag))
