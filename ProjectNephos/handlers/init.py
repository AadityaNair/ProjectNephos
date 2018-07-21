from ProjectNephos.backends import DataStore
from ProjectNephos.config import (
    Configuration,
    CONFIG_FULL_PATH_DEFAULT,
    BASE_FOLDER,
    default_values,
)
from ProjectNephos.handlers.base import BaseHandler
from ProjectNephos.orchestration import Server
from argparse import _SubParsersAction, Namespace
from logging import getLogger

from configparser import ConfigParser
from os.path import expanduser
import os

logger = getLogger(__name__)


class InitHandler(BaseHandler):
    """
    Handles startup of the project. This probably needs to be run just once.
    This performs the following tasks:
        1.  Creates all the config files and stuff.
        2.  Performs OAuth with google.
        3.  Starts an orchestration server that ensures that the recorder is always running.
            and other stuff not currently decided.
    TODO: Passing config to this handler should override create config option.

    NOTE: 2 is being handled separately as of now. It will be moved here later.
    """

    def _create_config(self, config_path):
        if config_path == CONFIG_FULL_PATH_DEFAULT:
            logger.debug("Default config path is being used")
            if not os.path.isfile(expanduser(config_path)):
                logger.debug("No previous file exists. Creating new one.")

                os.makedirs(expanduser(BASE_FOLDER), exist_ok=True)
                with open(CONFIG_FULL_PATH_DEFAULT, "w") as f:
                    c = ConfigParser()
                    c.read_dict(default_values)
                    c.write(f)
                logger.debug("Default config written")

        self.config = Configuration(CONFIG_FULL_PATH_DEFAULT)

    def run(self, args):
        logger.debug("Starting initial run.")

        self._create_config(args.config)

        logger.debug("Starting OAuth with Google.")
        DataStore(self.config)
        logger.debug("OAuth completed.")

        logger.debug("Starting Orchestration.")
        Server(self.config).run_server()
