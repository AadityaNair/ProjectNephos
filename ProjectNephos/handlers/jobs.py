from argparse import _SubParsersAction, Namespace
from logging import getLogger

from ProjectNephos.backends import DBStorage
from ProjectNephos.config import Configuration

logger = getLogger(__name__)


class JobHandler(object):
    """
    Handles creating new jobs. Each job is defined, at minimum, by the channel name,
    start time of the job, and the duration of the recording.

    Additionally, one can specify what actions can be performed on the recorded items.
    These actions currently are `upload`, `convert-to` and `tag`.
    `upload` makes sure that the file is uploaded to google drive.
    `convert-to` converts the file from one format to another.
    `tag` add the specified tags to the uploaded file.

    No matter what order you specify, these actions are performed in the order
    of convert-to -> upload -> tag. If one action is not specified, others will
    still carry on with the exception of tag. If upload is not specified, tag will
    not be performed.
    """

    def __init__(self, subcommand):
        self.subcommand = subcommand

    def init_with_config(self, config: Configuration):
        self.config = config
        self.db = DBStorage(config)

    def init_args(self, subparser: _SubParsersAction):
        parser = subparser.add_parser(self.subcommand)

        parser.add_argument("channel", action="store", help="Name of the channel")
        parser.add_argument("name", action="store", help="Name of the program")

        parser.add_argument(
            "start", action="store", help="Start time of the job in cron format"
        )
        parser.add_argument(
            "duration",
            action="store",
            help="How long do you want to record. In minutes",
            type=int,
        )

        parser.add_argument(
            "--upload",
            action="store_true",
            help="Set if you want to upload to Google Drive",
        )
        parser.add_argument(
            "--convert_to",
            action="store",
            help="Format you want to convert the file to.",
        )
        parser.add_argument(
            "--tags",
            action="store",
            nargs="*",
            help="Start time of the job in cron format",
        )

    def execute_command(self):
        pass

    def run(self, args: Namespace):
        self.db.add_job(
            args.name,
            args.channel,
            args.start,
            args.duration,
            args.upload,
            args.convert_to,
            args.tags,
        )
