import subprocess

from ProjectNephos.exceptions import FileNotFound
from ProjectNephos.handlers.base import BaseHandler

from argparse import _SubParsersAction, Namespace
from logging import getLogger
from os.path import isfile
import ffmpy


logger = getLogger(__name__)


class ProcessHandler(BaseHandler):
    """
    This class handles conversion of downloaded data. The recorded data will most likely
    be compressed to save space. The only functionality this class provides as of now is to
    take an input file and save an converted file.

    This does not delete the original file as of now.
    The conversion format is inferred from the name/extension of the output file, so make
    sure to name it correctly
    """

    def init_args(self, subparser):
        parser = super().init_args(subparser)

        parser.add_argument(
            "input_file", action="store", help="The file that has to be transformed"
        )
        parser.add_argument(
            "output_file", action="store", help="Final form of the file."
        )

    def run(self, args):
        if not isfile(args.input_file):
            logger.critical("Input file does not exist. Exiting")
            raise FileNotFound("Unable to find file.")

        ff = ffmpy.FFmpeg(
            inputs={args.input_file: None}, outputs={args.output_file: None}
        )
        ff.run()

    def execute_command(self, input_file, output_file):
        command = "ffmpeg -i {input} {output}".format(
            input=input_file, output=output_file
        )

        process = subprocess.Popen(
            command.split(), stderr=subprocess.STDOUT, stdout=subprocess.PIPE
        )
        stdout, _ = process.communicate()
        return stdout.decode("ascii")

    def execute_ccextractor(self, input_file, output_file):
        command = "{ccextractor} {input} -o {output}".format(
            ccextractor=self.config["recording", "ccextractor"],
            input=input_file,
            output=output_file,
        )
        process = subprocess.Popen(
                command.split(), stderr=subprocess.STDOUT, stdout=subprocess.PIPE
        )
        stdout, _ = process.communicate()
        return stdout.decode("ascii")
