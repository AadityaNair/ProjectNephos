from ProjectNephos.handlers.channels import ChannelHandler

from mock import MagicMock, patch, sentinel
import pytest

MODULE_NAME = "ProjectNephos.handlers.channels"


@patch(MODULE_NAME + ".BaseHandler.init_with_config")
@patch(MODULE_NAME + ".DBStorage")
def test_default_object(DBStorage, super_init_with_config):
    config = sentinel.config
    subc = sentinel.subc
    DBStorage.return_value = sentinel.db

    ch = ChannelHandler(subc, config)

    super_init_with_config.assert_called_once()
    DBStorage.assert_called_once_with(sentinel.config)
    assert ch.db == sentinel.db


@pytest.fixture
@patch(MODULE_NAME + ".DBStorage")
def default_object(_):
    ch = ChannelHandler(config=sentinel.config)
    return ch, ch.db


def test_run_list(default_object):
    ch, db = default_object

    args = MagicMock()
    args.action = "list"

    ch.run(args)

    db.get_channels.assert_called_once()


def test_run_no_name(default_object):
    ch, db = default_object

    args = MagicMock()
    args.action = "add"
    args.name = None
    args.ip = "1.2.3.4"

    ch.run(args)
    db.get_channels.assert_not_called()
    db.add_channel.assert_not_called()


def test_run_no_ip(default_object):
    ch, db = default_object

    args = MagicMock()
    args.action = "add"
    args.name = "asdf"
    args.ip = None

    ch.run(args)
    db.get_channels.assert_not_called()
    db.add_channel.assert_not_called()


def test_run_normal(default_object):
    ch, db = default_object

    args = MagicMock()
    args.action = "add"
    args.ip = "1.2.3.4"
    args.name = "asdf"

    ch.run(args)
    db.get_channels.assert_not_called()
    db.add_channel.assert_called_once_with("asdf", "1.2.3.4")
