from argparse import _SubParsersAction, Namespace

from ProjectNephos.config import Configuration
from ProjectNephos.exceptions import SubCommandNotFound

from logging import getLogger


logger = getLogger(__name__)


class BaseHandler(object):
    """
    This is the base class for all handlers. All common
    functions are defined here.
    """

    def __init__(self, subcommand: str = None, config: Configuration = None):
        """
        Initialise the handler. This generally takes the subcommand name when calling
        nephos from the command line. Config can also be provided in which case it will
        initialize config as well.
        """
        self.subcommand = subcommand
        self.config = config

        if self.config:
            self.init_with_config(self.config)

    def init_with_config(self, config):
        """
        Config is generally not available during the initialisation phase. This command is
        to be used in such a case.
        """
        if self.config != config and self.config is not None:
            logger.warning(
                "The class is already initalised with an config. Reinitializing with another one"
            )
        self.config = config

    def init_args(self, subparser: _SubParsersAction):
        """
        This command takes the subparser from the calling code and initialises the
        command line arguments for this function. This function will not be called when
        the handler isn't called from the command line.
        """
        if self.subcommand is None:
            raise SubCommandNotFound(
                "Subcommand has not been supplied. Cannot init_args without a subcommand"
            )
        return subparser.add_parser(self.subcommand)

    def execute_command(self):
        """
        Actually execute the functionality of the handler. The signature of the function
        will be different for each handler. This will be the function called when handler
        is not initiated from the command line.
        """
        raise NotImplementedError

    def run(self, args: Namespace):
        """
        This command is only used in the case of command line invocation. This will recieve
        the parsed command-line arguments and perform logic on them. For the most part, it
        will use the arguments to directly call the execute_command function and pretty print
        its output.

        Its signature will not change across handlers.
        """
        raise NotImplementedError
