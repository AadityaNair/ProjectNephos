from ProjectNephos.backends.DataBase import DBStorage

from mock import MagicMock, patch, sentinel
import pytest

MODULE_NAME = "ProjectNephos.backends.DataBase"


@patch(MODULE_NAME + ".sessionmaker")
@patch(MODULE_NAME + ".Base.metadata")
@patch(MODULE_NAME + ".create_engine")
def test_default_object(create_engine, metadata, sessionmaker):
    config = {("recording", "db_location"): "random1"}
    create_engine.return_value = sentinel.engine = MagicMock()

    Session = MagicMock()
    sessionmaker.return_value = Session

    d = DBStorage(config)

    assert d.config == config
    assert d.engine == sentinel.engine
    assert d.session == Session()

    create_engine.assert_called_once_with("sqlite:///random1")
    metadata.create_all.assert_called_once_with(sentinel.engine)
    Session.configure.assert_called_once_with(bind=sentinel.engine)


@pytest.fixture
@patch(MODULE_NAME + ".sessionmaker")
@patch(MODULE_NAME + ".Base.metadata")
@patch(MODULE_NAME + ".create_engine")
def default_object(*_):
    """
    Create an entire new session and DB object for each test
    """
    config = MagicMock()
    db = DBStorage(config)

    return db, db.session


def test_permissions_invalid_role(default_object):
    db, session = default_object
    tags = [1]

    with pytest.raises(AssertionError):
        db.add_permissions(tags, "random_email", "random_role")


def test_permissions(default_object):
    db, session = default_object
    tags = [1, 2, 3, 4, 5]

    db.add_permissions(tags, "random_email", "reader")

    assert session.add.call_count == len(tags)
    session.commit.assert_called_once()
