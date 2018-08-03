from ProjectNephos.handlers.upload import UploadHandler

from mock import MagicMock, patch
import pytest

MODULE_NAME = "ProjectNephos.handlers.upload"


@patch(MODULE_NAME + ".DataStore")
def test_default(ds):
    ds.return_value = "random_drive_store"
    sh = UploadHandler("random_subcommand")
    sh.init_with_config("random_config")

    assert sh.subcommand == "random_subcommand"
    assert sh.backend == "random_drive_store"
    ds.assert_called_once_with("random_config")


@pytest.fixture
@patch(MODULE_NAME + ".DataStore")
def default_object(ds):
    backend = MagicMock()
    ds.return_value = backend

    obj = UploadHandler("random")
    obj.init_with_config("random")

    return obj, backend


@patch(MODULE_NAME + ".path.isfile")
def test_return_nothing(isfile, default_object):
    uh, _ = default_object

    args = MagicMock()
    args.ignore_errors = True
    args.files = ["random1", "random2"]

    isfile.return_value = False
    assert uh.run(args) is None
    assert isfile.call_count == 2
