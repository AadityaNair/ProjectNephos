from ProjectNephos.handlers.process import ProcessHandler
from ProjectNephos.exceptions import FileNotFound

from mock import MagicMock, patch
import pytest

MODULE_NAME = "ProjectNephos.handlers.process"


def test_default():
    sh = ProcessHandler("random_subcommand", "random_config")

    assert sh.subcommand == "random_subcommand"
    assert sh.config == "random_config"


@patch(MODULE_NAME + ".isfile")
def test_bad_file(isfile):
    args = MagicMock()
    args.input_file = "random_input1"
    isfile.return_value = False

    sh = ProcessHandler("random_subcommand", "random_config")

    with pytest.raises(FileNotFound):
        sh.run(args)
    isfile.assert_called_once_with("random_input1")
