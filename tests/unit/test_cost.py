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
    assert Cost(Settings())._runner_type_job(job_request) == "self-hosted"

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
    assert Cost(Settings())._runner_type_job(job_request) == "github-hosted"

def test_get_job_cost():
    settings = Settings()

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
        started_at=datetime.datetime(2022, 5, 4, 9, 0),
        completed_at=datetime.datetime(2022, 5, 4, 10, 0),
        name="1",
        labels=[
            "ubuntu-latest",
            "self-hosted"
        ]
    )
    assert Cost(settings)._get_job_cost(job_request, "large") == 0.96

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
        started_at=datetime.datetime(2022, 5, 4, 10, 0),
        completed_at=datetime.datetime(2022, 5, 4, 10, 30),
        name="1",
        labels=[
            "self-hosted"
        ]
    )
    assert Cost(settings)._get_job_cost(job_request, "flavor") == 0.24
