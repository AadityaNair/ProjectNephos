from ProjectNephos.orchestration.server import Server
from mock import MagicMock, patch, sentinel
import pytest

MODULE_NAME = "ProjectNephos.orchestration.server"


@patch(MODULE_NAME + ".DBStorage")
@patch(MODULE_NAME + ".Server.JOB_LIST")
@patch(MODULE_NAME + ".BlockingScheduler")
def test_default_object(BS, JOB_LIST, _):

    obj = Server(sentinel.config)

    assert obj.config == sentinel.config
    assert obj.jobs == JOB_LIST
    BS.assert_called_once()


@pytest.fixture
@patch(MODULE_NAME + ".DBStorage")
@patch(MODULE_NAME + ".Server.JOB_LIST")
@patch(MODULE_NAME + ".BlockingScheduler")
def default_object(*_):
    obj = Server(sentinel.config)
    return obj, obj.sched


def test_regular_job(default_object):
    s, sch = default_object
    s.jobs = [1, 2, 3, 4]

    s.add_regular_jobs()
    assert sch.add_job.call_count == len(s.jobs)


def test_recording_job(default_object):
    s, sch = default_object
    rec_list = [MagicMock()] * 5
    s.db.get_job.return_value = rec_list

    s.add_recording_jobs()
    assert sch.add_job.call_count == len(rec_list)


@patch(MODULE_NAME + ".Server.add_regular_jobs")
@patch(MODULE_NAME + ".Server.add_recording_jobs")
def test_run_server(rec_job, reg_job, default_object):
    s, sch = default_object
    s.run_server()

    rec_job.assert_called_once()
    reg_job.assert_called_once()
    sch.start.assert_called_once()
