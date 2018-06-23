from ProjectNephos.handlers.tag import TagHandler

from mock import patch

MODULE_NAME = "ProjectNephos.handlers.tag"


@patch(MODULE_NAME + ".SearchHandler")
@patch(MODULE_NAME + ".DriveStorage")
def test_default(ds, _):
    ds.return_value = "random_drive_store"
    sh = TagHandler("random_subcommand")
    sh.init_with_config("random_config")

    assert sh.subcommand == "random_subcommand"
    assert sh.backend == "random_drive_store"
    ds.assert_called_once_with("random_config")
