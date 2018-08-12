from logging import getLogger
from ProjectNephos.backends import DBStorage

from ProjectNephos.handlers.base import BaseHandler

logger = getLogger(__name__)


class ScheduleHandler(BaseHandler):
    """
    Add or list channel schedules.
    The channel should already have been added to Nephos.
    """

    def init_with_config(self, config):
        super().init_with_config(config)
        self.db = DBStorage(config)

    def init_args(self, subparser):
        parser = super().init_args(subparser)

        parser.add_argument(
            "action", help="Define what action to take.", choices=["list", "add"]
        )

        parser.add_argument("--channel", action="store", help="Name of the channel")
        parser.add_argument("--name", action="store", help="Name of the program")

        parser.add_argument(
            "--start", action="store", help="Start time of the program in cron format"
        )
        parser.add_argument(
            "--duration",
            action="store",
            help="How long the program is. In minutes",
            type=int,
        )

        parser.add_argument(
            "--tags",
            action="store",
            nargs="+",
            help="Tags that should be associated with the program.",
        )

        def run(self, args):
            if args.action == "add":
                if not all([args.channel, args.name, args.start, args.duration]):
                    logger.critical(
                        "All of the following options are required: --channel, --name, --start, --duration"
                    )
                    return -1

                if self.db.get_channels(name=args.channel) is None:
                    logger.critical(
                        "Provided channel name does not exist. Please provide a correct one."
                    )
                    return -1

                self.db.add_schedule(
                    args.name, args.channel, args.start, args.duration, args.tags
                )

            if args.action == "list":
                for items in self.db.get_schedule_items():
                    print(items)
