from ProjectNephos.backends.GDrive import DriveStorage
from ProjectNephos.exceptions import OAuthFailure, FileNotFound
from mock import MagicMock, patch

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

    g = DriveStorage()
    creds.authorize.assert_called_once_with("random1")

    build.assert_called_with("drive", "v3", http=authorized_http)

    service.files.assert_called_once()
    service.permissions.assert_called_once()

    assert g.file_service == "random2"
    assert g.perm_service == "random3"


def test_credentials_preexisting():
    pass


def test_credentials_flow_invalid_secret():
    pass


def test_credentials_flow_bad_json():
    pass


def test_credentials_flow_bad_code():
    pass


def test_credentials_flow_success():
    pass


def test_exists_yes():
    pass


def test_exists_no():
    pass


def test_write():
    pass


def test_write_nonexistant():
    pass


def test_read():
    pass


def test_read_nonexistant():
    pass


def test_delete():
    pass


def test_search():
    pass


def test_search_no_result():
    pass


def test_add_perms():
    pass


def test_add_perms_no_file():
    pass
