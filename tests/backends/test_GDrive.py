from googleapiclient.errors import HttpError

from ProjectNephos.backends.GDrive import DriveStorage
from ProjectNephos.exceptions import OAuthFailure, FileNotFound
from mock import MagicMock, patch
import pytest

MODULE_NAME = "ProjectNephos.backends.GDrive"


@patch(MODULE_NAME + ".discovery.build")
@patch(MODULE_NAME + ".Http")
@patch(MODULE_NAME + ".DriveStorage._get_credentials")
def test_default_object_creation(getc, Http, build):
    creds = MagicMock()
    authorized_http = MagicMock()
    creds.authorize.return_value = authorized_http
    getc.return_value = creds

    Http.return_value = "random1"

    service = MagicMock()
    service.files.return_value = "random2"
    service.permissions.return_value = "random3"
    build.return_value = service

    config = {
        "google": {
            "auth_token_location": "random4",
            "client_secret_location": "random5",
        }
    }
    g = DriveStorage(config)

    getc.assert_called_once_with(credential_path="random4", client_secret_loc="random5")
    creds.authorize.assert_called_once_with("random1")
    build.assert_called_with("drive", "v3", http=authorized_http)
    service.files.assert_called_once()
    service.permissions.assert_called_once()

    assert g.file_service == "random2"
    assert g.perm_service == "random3"


@patch(MODULE_NAME + ".discovery.build")
@patch(MODULE_NAME + ".Http")
@patch(MODULE_NAME + ".Storage")
@patch(MODULE_NAME + ".DriveStorage._run_credentials_flow")
def test_credentials_preexisting(runcf, Storage, *_):
    creds = MagicMock()
    creds.invalid = False
    store = MagicMock()
    store.get.return_value = creds
    Storage.return_value = store

    DriveStorage(MagicMock())

    Storage.assert_called_once()
    store.get.assert_called_once()
    runcf.assert_not_called()


def test_credentials_flow_invalid_secret():
    pass


def test_credentials_flow_bad_json():
    pass


def test_credentials_flow_bad_code():
    pass


def test_credentials_flow_success():
    pass


@pytest.fixture
@patch(MODULE_NAME + ".Http")
@patch(MODULE_NAME + ".DriveStorage._get_credentials")
@patch(MODULE_NAME + ".discovery.build")
def default_object(build, *_):
    file_service = MagicMock()
    perm_service = MagicMock()

    service = MagicMock()
    service.files.return_value = file_service
    service.permissions.return_value = perm_service
    build.return_value = service
    g = DriveStorage(MagicMock())
    return g, file_service, perm_service


def test_exists_yes(default_object):
    g, file_service, _ = default_object

    exc = MagicMock()
    file_service.get.return_value = exc
    ret = g.is_exists("random1")

    assert ret
    file_service.get.assert_called_once_with(fileId="random1")
    exc.execute.assert_called_once()


def test_exists_no(default_object):
    g, file_service, _ = default_object

    exc = MagicMock()
    exc.execute.side_effect = HttpError("random2", b"random3")
    file_service.get.return_value = exc
    ret = g.is_exists("random1")

    assert not ret
    file_service.get.assert_called_once_with(fileId="random1")
    exc.execute.assert_called_once()


def test_write():
    pass


@patch(MODULE_NAME + ".isfile")
def test_write_nonexistant(isfile, default_object):
    g, _, _ = default_object

    isfile.return_value = False
    with pytest.raises(FileNotFound):
        g.write("random1")
    isfile.assert_called_with("random1")


def test_read():
    pass


@patch(MODULE_NAME + ".DriveStorage.is_exists")
def test_read_nonexistant(is_exists, default_object):
    g, _, _ = default_object

    is_exists.return_value = False
    with pytest.raises(FileNotFound):
        g.read("random1")
    is_exists.assert_called_with("random1")


def test_delete():
    pass


def test_search():
    pass


def test_search_no_result():
    pass


def test_add_perms():
    pass


@patch(MODULE_NAME + ".DriveStorage.is_exists")
def test_add_perms_no_file(is_exists, default_object):
    g, _, _ = default_object

    is_exists.return_value = False
    with pytest.raises(FileNotFound):
        g.add_permissions_user("random1", "email", "role")
    is_exists.assert_called_with("random1")
