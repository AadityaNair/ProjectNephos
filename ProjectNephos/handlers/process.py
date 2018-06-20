from ProjectNephos.exceptions import FileNotFound

from configparser import ConfigParser
from argparse import _SubParsersAction, Namespace
from logging import getLogger
from os.path import isfile
import ffmpy

logger = getLogger(__name__)


class ProcessHandler(object):
    """
    This class handles conversion of downloaded data. The recorded data will most likely
    be compressed to save space. The only functionality this class provides as of now is to
    take an input file and save an converted file.

    This does not delete the original file as of now.
    The conversion format is inferred from the name/extension of the output file, so make
    sure to name it correctly
    """

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
