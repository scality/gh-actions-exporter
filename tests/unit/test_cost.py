import datetime
import pytest

from unittest.mock import MagicMock
from gh_actions_exporter.cost import Cost
from gh_actions_exporter.config import Settings


@pytest.fixture
def headers():
    headers = {
        'X-Github-Event': 'workflow_run'
    }
    return headers

def test_runner_type_job(mocker):
    job_request: dict = {
        "labels": [
            "large",
            "jammy",
            "self-hosted"
        ]
    }
    assert Cost(Settings())._runner_type_job(job_request) == "self-hosted"

    job_request: dict = {
        "labels": [
            "ubuntu-latest"
        ]
    }
    assert Cost(Settings())._runner_type_job(job_request) == "github-hosted"

def test_get_job_cost():
    settings = Settings()

    job_request = {
        "completed_at": datetime.datetime(2022, 5, 4, 10, 0),
        "started_at": datetime.datetime(2022, 5, 4, 9, 0),
        "name": "greet (tata)",
        "labels": ["large", "self-hosted"]
    }
    assert Cost(settings)._get_job_cost(job_request, "large") == 0.96

    job_request = {
        "completed_at": datetime.datetime(2022, 5, 4, 10, 30),
        "started_at": datetime.datetime(2022, 5, 4, 10, 0),
        "name": "greet (tata)",
        "labels": ["ubuntu-latest"]
    }
    assert Cost(settings)._get_job_cost(job_request, "flavor") == 0.24

    job_request = {
        "completed_at": datetime.datetime(2022, 5, 4, 10, 30),
        "started_at": datetime.datetime(2022, 5, 4, 10, 0),
        "name": "greet (tata)",
        "labels": ["self-hosted"]
    }
    assert Cost(settings)._get_job_cost(job_request, "flavor") == 0.24

def test_get_workflow_jobs_url(mocker):
    webhook = MagicMock()
    webhook.repository.full_name = "owner/repo"
    webhook.workflow_run.id = "42"

    obj = Cost(Settings())
    url = obj._get_workflow_jobs_url(webhook)

    expected_url = "/repos/owner/repo/actions/runs/42/jobs"
    assert url == expected_url

def test_get_previous_check_run(mocker):
    repository = MagicMock()
    webhook = MagicMock()
    settings = Settings()
    webhook.repository.full_name = "owner/repo"
    webhook.workflow_run.head_sha = "abc123"

    fake_result = {
        "check_runs": [
            {
                "name": settings.title,
                "app": {"id": settings.github_app_id},
                "output": {"summary": settings.summary}
            }
        ]
    }

    mocker.patch.object(repository._requester, "requestJsonAndCheck", return_value=(200, fake_result))
    assert Cost(Settings())._get_previous_check_run(repository, webhook) == settings.summary
