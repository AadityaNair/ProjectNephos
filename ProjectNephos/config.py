import logging
import os
from configparser import ConfigParser
from io import StringIO
from logging import getLogger

logger = getLogger(__name__)

# These values will be applied when there is no config file specified.
default_values = {

    'google': {
        'client_secret_location': '~/client_secret.json',
        'auth_token_location': '~/.credentials/',
    },

    'downloads': {
        'local_save_location': '~/nephos/'
    },
}

USER_CONFIG_LOC = '/tmp/test/'  # TODO: Fill better info at the end
USER_CONFIG_FNAME = 'config.ini'
config = ConfigParser()


def parse_config() -> ConfigParser:
    full_path = USER_CONFIG_LOC + USER_CONFIG_FNAME

    if not os.path.isfile(full_path):
        config.read_dict(default_values)
        logger.info("Config file does not exist. Creating a new one at {}".format(USER_CONFIG_LOC))

        os.makedirs(USER_CONFIG_LOC, exist_ok=True)
        with open(full_path, 'w') as f:
            config.write(f)
    else:
        config.read(full_path)
        logger.info("Config found and read")
        ini = StringIO()
        config.write(ini)
        logger.debug("Following config was read")
        logger.debug(ini.getvalue())

    return config
