from ProjectNephos.orchestration.tasks import *

from mock import MagicMock, patch, sentinel
import pytest

MODULE_NAME = "ProjectNephos.orchestration.tasks"


@patch(MODULE_NAME + ".ProcessHandler")
def test_process_job(ph):
    config = {("downloads", "temp_save_location"): "/temp1/temp2/"}
    ret = process_job("rnd1", "/test1/test2/fname.abc", config)

    assert ret == "/temp1/temp2/fname.rnd1"
    ph().execute_command.assert_called_once()


@patch(MODULE_NAME + ".ProcessHandler")
def test_process_job_no(ph):
    config = {("downloads", "temp_save_location"): "/temp1/temp2/"}
    ret = process_job(False, "/test1/test2/fname.abc", config)

    assert ret == "/test1/test2/fname.abc"
    ph().execute_command.assert_not_called()
