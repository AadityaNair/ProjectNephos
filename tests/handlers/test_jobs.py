from ProjectNephos.handlers.jobs import JobHandler

from mock import MagicMock, patch, sentinel
import pytest

MODULE_NAME = "ProjectNephos.handlers.jobs"


@pytest.fixture
@patch(MODULE_NAME + ".DBStorage")
def default_object(_):
    ch = JobHandler(config=sentinel.config)

    args = MagicMock()
    args.action = None
    args.channel, args.name, args.start, args.duration, args.program_tags = [None] * 5

    return ch, ch.db, args


def test_list(default_object):
    jb, db, args = default_object

    args.action = "list"
    jb.run(args)
    db.get_job.assert_called()


def test_add_bad_arguments(default_object):
    jb, db, args = default_object

    args.action = "add"
    assert jb.run(args) == -1
    db.add_job.assert_not_called()


def test_add_bad_channel(default_object):
    jb, db, args = default_object

    args.action = "add"
    args.channel, args.name, args.start, args.duration = (
        "random1",
        "rand2",
        "rand3",
        "rand4",
    )

    db.get_channels.return_value = []
    assert jb.run(args) == -1
    db.add_job.assert_not_called()
    db.get_channels.assert_called_with(name="random1")


def test_add_bad_job(default_object):
    jb, db, args = default_object

    args.action = "add"
    args.channel, args.name, args.start, args.duration = (
        "random1",
        "rand2",
        "rand3",
        "rand4",
    )

    db.get_job.return_value = "random"
    db.get_channels.return_value = [1]
    assert jb.run(args) == -1
    db.add_job.assert_not_called()
    db.get_job.assert_called_with(jobname="rand2")


def test_add_job(default_object):
    jb, db, args = default_object

    args.action = "add"
    args.channel, args.name, args.start, args.duration = (
        "random1",
        "rand2",
        "rand3",
        "rand4",
    )

    db.get_job.return_value = None
    db.get_channels.return_value = [1]
    jb.run(args)
    db.add_job.assert_called()
