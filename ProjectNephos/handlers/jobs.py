from argparse import _SubParsersAction, Namespace
from logging import getLogger

from ProjectNephos.backends import DBStorage
from ProjectNephos.config import Configuration
from ProjectNephos.handlers.base import BaseHandler

logger = getLogger(__name__)


class JobHandler(BaseHandler):
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
            "--start", action="store", help="Start time of the job in cron format"
        )
        parser.add_argument(
            "--duration",
            action="store",
            help="How long do you want to record. In minutes",
            type=int,
        )

        parser.add_argument(
            "--program_tags",
            action="store",
            nargs="+",
            help="If program schedule is updated, use this download all programs with a given tag."
            " Ignores --channel, --start and --duration",
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
            "--subtitles",
            action="store_true",
            help="Set if you also want to extract subtitles",
        )
        parser.add_argument(
            "--tags",
            action="store",
            nargs="*",
            help="Tags you want to upload the file with",
        )

    def run(self, args):
        if args.action == "add":
            if not args.program_tags:
                if not all([args.channel, args.name, args.start, args.duration]):
                    logger.critical(
                        "All of the following options are required: --channel, --name, --start, --duration"
                    )
                    return -1

                if len(self.db.get_channels(name=args.channel)) == 0:
                    logger.critical(
                        "Provided channel name does not exist. Please provide a correct one."
                    )
                    return -1
                if self.db.get_job(jobname=args.name) is not None:
                    logger.critical(
                        "There is already a job by that name. Choose a different name."
                    )
                    return -1

                self.db.add_job(
                    args.name,
                    args.channel,
                    args.start,
                    args.duration,
                    args.upload,
                    args.convert_to,
                    args.subtiles,
                    args.tags,
                )
            else:
                if not args.name:
                    logger.critical("Job name is required.")
                    return -1
                if self.db.get_job(jobname=args.name) is not None:
                    logger.critical(
                        "There is already a job by that name. Choose a different name."
                    )
                    return -1
                individual_programs = self.db.get_schedule_items(tags=args.program_tags)
                for prog in individual_programs:
                    self.db.add_job(
                        args.name + "->" + prog.program,
                        prog.channel,
                        prog.start,
                        prog.duration,
                        args.upload,
                        args.convert_to,
                        args.subtitles,
                        args.tags,
                    )

        if args.action == "list":
            for items in self.db.get_job():
                print(items)
