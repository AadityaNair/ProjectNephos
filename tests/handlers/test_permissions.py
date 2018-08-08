from ProjectNephos.handlers.permissions import PermissionHandler

from mock import MagicMock, patch, sentinel
import pytest

MODULE_NAME = "ProjectNephos.handlers.permissions"


@pytest.fixture
@patch(MODULE_NAME + ".DBStorage")
def default_object(_):
    ph = PermissionHandler(config=sentinel.config)

    args = MagicMock()
    args.action = None
    args.for_tags, args.share_with, args.not_persistent = [None] * 3

    return ph, ph.db, args

