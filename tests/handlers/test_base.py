from ProjectNephos.exceptions import SubCommandNotFound
from ProjectNephos.handlers.base import BaseHandler

from mock import MagicMock, patch, sentinel
import pytest

MODULE_NAME = "ProjectNephos.handlers.base"


@patch(MODULE_NAME + ".BaseHandler.init_with_config")
def test_default_object_with_config(init_with_config):
    config = sentinel.config
    subc = sentinel.subcommand

    b = BaseHandler(subc, config)

    assert b.config == config
    assert b.subcommand == subc
    init_with_config.assert_called_once_with(config)


@patch(MODULE_NAME + ".BaseHandler.init_with_config")
def test_default_object_no_config(init_with_config):
    b = BaseHandler(sentinel.subcommand)

    assert b.config is None
    assert b.subcommand == sentinel.subcommand
    init_with_config.assert_not_called()


def test_default_object_with_init_config():
    config = sentinel.config
    subc = sentinel.subcommand

    b = BaseHandler(subc)
    b.init_with_config(config)

    assert b.config == config


def test_init_args_no_subcommand():
    b = BaseHandler()
    assert b.subcommand is None

    subparser = MagicMock()
    with pytest.raises(SubCommandNotFound):
        b.init_args(subparser)


def test_init_args_subcommand():
    b = BaseHandler(sentinel.subcommand)

    assert b.subcommand == sentinel.subcommand

    subparser = MagicMock()
    b.init_args(subparser)

    subparser.add_parser.assert_called_once_with(sentinel.subcommand)


def test_execute_command():
    b = BaseHandler()

    with pytest.raises(NotImplementedError):
        b.execute_command()


def test_run():
    b = BaseHandler()

    with pytest.raises(NotImplementedError):
        b.run(MagicMock())
