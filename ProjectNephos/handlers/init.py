from ProjectNephos.backends.GDrive import DriveStorage
from ProjectNephos.orchestration import Server
from argparse import _SubParsersAction
from configparser import ConfigParser
from multiprocessing import Process
from logging import getLogger

logger = getLogger(__name__)


class InitHandler(object):
    """
    Handles startup of the project. This probably needs to be run just once.
    This performs the following tasks:
        1.  Creates all the config files and stuff.
        2.  Performs OAuth with google.
        3.  Starts an orchestration server that ensures that the recorder is always running.
            and other stuff not currently decided.

    NOTE: 1 and 2 are being handled separately as of now. They will be moved here later.
    """

    def __init__(self, subcommand: str, config: ConfigParser):
        self.subcommand = subcommand
        self.config = config

    def _init_args(self, subparser: _SubParsersAction):
        subparser.add_parser(self.subcommand)

    def run(self):
        logger.debug("Starting initial run.")
        logger.debug("Completing OAuth with Google.")
        DriveStorage()
        logger.debug("OAuth completed.")

        logger.debug("Starting Orchestration.")

        p = Process(target=Server, args=(1, 2, 3))
        p.start()
        logger.debug("Orchestration Started")
