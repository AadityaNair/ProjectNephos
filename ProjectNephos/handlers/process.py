from ProjectNephos.exceptions import FileNotFound

from configparser import ConfigParser
from argparse import _SubParsersAction, Namespace
from logging import getLogger
from os.path import isfile
import ffmpy

logger = getLogger(__name__)


class ProcessHandler(object):

    def __init__(self, subcommand: str, config: ConfigParser):
        self.subcommand = subcommand
        self.config = config

    def _init_args(self, subparser: _SubParsersAction):
        parser = subparser.add_parser(self.subcommand)

        parser.add_argument(
            "input_file", action="store", help="The file that has to be transformed"
        )
        parser.add_argument(
            "output_file", action="store", help="Final form of the file."
        )

    def run(self, args: Namespace):
        if not isfile(args.input_file):
            logger.critical("Input file does not exist. Exiting")
            raise FileNotFound("Unable to find file.")

        ff = ffmpy.FFmpeg(
            inputs={args.input_file: None}, outputs={args.output_file: None}
        )
        ff.run()
