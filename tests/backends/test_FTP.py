from ProjectNephos.backends.FTP import FTPStorage

from mock import MagicMock, patch, sentinel
import pytest

from ProjectNephos.exceptions import FileNotFound

MODULE_NAME = "ProjectNephos.backends.FTP"


@pytest.fixture
@patch(MODULE_NAME + ".ftplib.FTP")
def default_object(*_):
    config = MagicMock()
    obj = FTPStorage(config)

    return obj, obj.ftp


@patch(MODULE_NAME + ".isfile")
def test_write_nonexistant(isfile, default_object):
    f, _ = default_object

    isfile.return_value = False
    with pytest.raises(FileNotFound):
        f.write("random1")
    isfile.assert_called_with("random1")


def test_permissions(default_object):
    f, _ = default_object
    assert f.add_permission_user("asdf") is None
