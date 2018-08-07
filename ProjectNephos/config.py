import os
from configparser import ConfigParser, NoOptionError, NoSectionError
from logging import getLogger

from ProjectNephos.exceptions import FileNotFound

logger = getLogger(__name__)

# These values will be applied when there is no config file specified.
BASE_FOLDER = "~/aanair_nephos/.nephos"
default_values = {
    "google": {
        "client_secret_location": "~/aanair_nephos/ProjectNephos/client_secret.json",
        "auth_token_location": BASE_FOLDER + "/access.json",
    },
    "downloads": {
        "local_save_location": BASE_FOLDER + "/files/",
        "temp_save_location": BASE_FOLDER + "/temp_files/",
    },
    "recording": {
        "db_location": BASE_FOLDER + "/nephos.sqlite",
        "multicat": "~/multicat-2.1/multicat",
        "ccextractor": "~/aanair_nephos/ccextractor",
        "bind": "159.237.36.240",
        "logs": BASE_FOLDER + "/logs/",
    },
    "ftp": {
        "host": "localhost",
        "port": "2121",
        "username": "anonymous",
        "password": "password",
    },
    "mail": {
        "host": "smtp.server.com",
        "port": "25",
        "admin": "admin@ccextractor.org",
        "From": "nephos@ccextractor.org",
    },
    "others": {"backends": "google ftp"},
}

USER_CONFIG_LOC = BASE_FOLDER
USER_CONFIG_FNAME = "config.ini"
CONFIG_FULL_PATH_DEFAULT = os.path.expanduser(USER_CONFIG_LOC + "/" + USER_CONFIG_FNAME)
config = ConfigParser()


class Configuration(object):
    """
    This class handles all requests for the config information.
    It takes a path to a config file. If no path is provided, it will take the
    default values defined above.
    It also makes the following conversions,
        1. Change None, True, False strings into actual None, True, False booleans.
        2. All strings starting with ~ are converted to full path

    Takes:
        (optional) path to config file.
    Returns:
        Config object
    """

    def __init__(self, config_path=None):
        c = ConfigParser()

        # Load the default values first.
        c.read_dict(default_values)

        if config_path is not None:
            if not os.path.isfile(os.path.expanduser(config_path)):
                if config_path == CONFIG_FULL_PATH_DEFAULT:
                    raise FileNotFound(
                        "Default file not yet created. Try running `nephos init`"
                    )
                else:
                    raise FileNotFound("Specified config not found")
            else:
                c.read(config_path)

        self.conf_items = c

    def get(self, section, key):
        try:
            value = self.conf_items.get(section, key)
        except NoSectionError:
            raise NoSectionError("Section '{}' not found".format(section))
        except NoOptionError:
            raise NoOptionError(
                "Section '{}' does not contain a key '{}'".format(section, key)
            )

        if value == "None":
            return None
        if value == "False":
            return False
        if value == "True":
            return True
        if value.startswith("~"):
            return os.path.expanduser(value)
        return value

    def __getitem__(self, tup):
        return self.get(tup[0], tup[1])
