from ProjectNephos.handlers.search import SearchHandler

from mock import MagicMock, patch
import pytest

MODULE_NAME = "ProjectNephos.handlers.search"


@patch(MODULE_NAME + ".DriveStorage")
def test_default(ds):
    ds.return_value = "random_drive_store"

    sh = SearchHandler("random_subcommand", "random_config")

    assert sh.subcommand == "random_subcommand"
    assert sh.backend == "random_drive_store"
    ds.assert_called_once_with("random_config")
    print(ds.return_value)


@pytest.fixture
@patch(MODULE_NAME + ".DriveStorage")
def default_object(ds):
    backend = MagicMock()
    ds.return_value = backend

    obj = SearchHandler("random", "random")

    return obj, backend


def test_return_nothing(default_object):
    se, _ = default_object

    assert se.execute_command(None, None, True) is None
    assert se.execute_command(None, None, False) is None
