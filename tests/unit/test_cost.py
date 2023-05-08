import pytest
import datetime

from unittest.mock import MagicMock
from gh_actions_exporter.cost import Cost
from gh_actions_exporter.config import Settings
from gh_actions_exporter.types import WorkflowJob


@pytest.fixture
def headers():
    headers = {
        'X-Github-Event': 'workflow_run'
    }
    return headers

def test_runner_type_job(mocker):
    job_request = WorkflowJob(
        id=1,
        run_id=1,
        run_url="1",
        run_attempt=1,
        node_id="1",
        head_sha="1",
        url="1",
        html_url="1",
        status="1",
        started_at=datetime.datetime.now(),
        name="1",
        labels=[
            "large",
            "jammy",
            "self-hosted"
        ]
    )
    assert Cost(Settings())._runner_type_job(dict(job_request)) == "self-hosted"

    job_request = WorkflowJob(
        id=1,
        run_id=1,
        run_url="1",
        run_attempt=1,
        node_id="1",
        head_sha="1",
        url="1",
        html_url="1",
        status="1",
        started_at=datetime.datetime.now(),
        name="1",
        labels=[
            "ubuntu-latest"
        ]
    )
    assert Cost(Settings())._runner_type_job(dict(job_request)) == "github-hosted"

def test_get_job_cost():
    settings = Settings()

    job_request = {
        "id": 1,
        "run_id": 1,
        "run_url": "1",
        "run_attempt": 1,
        "node_id": "1",
        "head_sha": "1",
        "url": "1",
        "html_url": "1",
        "status": "1",
        "started_at": "2021-11-16T17:52:47Z",
        "completed_at": "2021-11-16T17:58:47Z",
        "name": "1",
        "labels": [
            "ubuntu-latest",
            "self-hosted"
        ]
    }
    assert Cost(settings)._get_job_cost(dict(job_request), "large") == 0.096

    job_request = {
        "id": 1,
        "run_id": 1,
        "run_url": "1",
        "run_attempt": 1,
        "node_id": "1",
        "head_sha": "1",
        "url": "1",
        "html_url": "1",
        "status": "1",
        "started_at": "2021-11-16T17:51:47Z",
        "completed_at": "2021-11-16T17:59:47Z",
        "name": "1",
        "labels": [
            "ubuntu-latest",
            "self-hosted"
        ]
    }
    assert Cost(settings)._get_job_cost(dict(job_request), "flavor") == 0.064
