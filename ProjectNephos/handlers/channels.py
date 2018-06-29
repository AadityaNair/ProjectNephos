from argparse import _SubParsersAction, Namespace
from logging import getLogger

from ProjectNephos.config import Configuration
from ProjectNephos.backends import DBStorage

logger = getLogger(__name__)


class ChannelHandler(object):
    """
    Handles creating channels.
    """

    def __init__(self, subcommand):
        self.subcommand = subcommand

    def init_with_config(self, config: Configuration):
        self.config = config
        self.db = DBStorage(config)

    def init_args(self, subparser: _SubParsersAction):
        parser = subparser.add_parser(self.subcommand)
        parser.add_argument(
            "action", help="Define what action to take.", choices=["list", "add"]
        )

        parser.add_argument("--name", action="store", help="Name of the channel")
        parser.add_argument("--ip", action="store", help="IP Address of the channel")

        parser.add_argument("--teletext", action="store", help="Teletext Page")
        parser.add_argument("--country", action="store", help="Country Code")
        parser.add_argument(
            "--timezome", action="store", help="Timezone of the channel"
        )
        parser.add_argument("--language", action="store", help="Language of the stream")
        parser.add_argument("--source", action="store", help="Source of the video.")

    def execute_command(self):
        pass

    def run(self, args: Namespace):
        if args.action == "add":
            if not args.name:
                logger.critical("--name is required. Try again.")
            elif not args.ip:
                logger.critical("--ip is required. Try again.")
            else:
                self.db.add_channel(args.name, args.ip)

        if args.action == "list":
            print(self.db.get_channels())
