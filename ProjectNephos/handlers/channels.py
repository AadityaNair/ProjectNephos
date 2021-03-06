from argparse import _SubParsersAction, Namespace
from logging import getLogger

from ProjectNephos.config import Configuration
from ProjectNephos.backends import DBStorage
from ProjectNephos.handlers.base import BaseHandler

logger = getLogger(__name__)


class ChannelHandler(BaseHandler):
    """
    Handles creating channels.
    """

    def init_with_config(self, config):
        super().init_with_config(config)

        self.db = DBStorage(config)

    def init_args(self, subparser):
        parser = super().init_args(subparser)

        parser.add_argument(
            "action", help="Define what action to take.", choices=["list", "add"]
        )

        parser.add_argument("--name", action="store", help="Name of the channel")
        parser.add_argument("--ip", action="store", help="IP Address of the channel")

    def run(self, args):
        if args.action == "add":
            if not args.name:
                logger.critical("--name is required. Try again.")
            elif not args.ip:
                logger.critical("--ip is required. Try again.")
            else:
                self.db.add_channel(args.name, args.ip)

        if args.action == "list":
            print(self.db.get_channels())
