import datetime
from unittest.mock import MagicMock

import pytest

from gh_actions_exporter.config import Settings
from gh_actions_exporter.cost import Cost
from gh_actions_exporter.types import WorkflowJob


@pytest.fixture
def headers():
    headers = {"X-Github-Event": "workflow_run"}
    return headers


def test_runner_type_job():
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
        labels=["large", "jammy", "self-hosted"],
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
        labels=["ubuntu-latest"],
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
        "labels": ["self-hosted"],
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
        "labels": ["self-hosted"],
    }
    assert Cost(settings)._get_job_cost(dict(job_request), "flavor") == 0.064


def test_get_workflow_jobs():
    g = MagicMock()
    settings = Settings()
    webhook = MagicMock()
    webhook.organization.login = "myorg"
    webhook.repository.name = "myrepo"
    webhook.workflow_run.id = 123

    g.rest.checks.list_for_ref.return_value.json.return_value = {
        "check_runs": [
            {
                "name": settings.title,
                "app": {"id": settings.github_app_id},
                "output": {"summary": "Previous summary"},
            },
            {
                "name": "Another check run",
                "app": {"id": 456},
                "output": {"summary": "Another summary"},
            },
        ]
    }

    cost = Cost(settings)
    summary = cost._get_previous_check_run(g, webhook)
    assert summary == "Previous summary"

    g.rest.checks.list_for_ref.return_value.json.return_value = {
        "check_runs": [
            {
                "name": settings.title,
                "app": {"id": 12},
                "output": {"summary": "Previous summary"},
            },
            {
                "name": "Another check run",
                "app": {"id": 456},
                "output": {"summary": "Another summary"},
            },
        ]
    }

    summary = cost._get_previous_check_run(g, webhook)
    assert summary == ""


def test_get_previous_check_run():
    g = MagicMock()
    webhook = MagicMock()
    settings = Settings()
    cost = Cost(settings)

    webhook.organization.login = "myorg"
    webhook.repository.name = "myrepo"
    webhook.workflow_run.head_sha = "1234567890abcdef"

    g.rest.checks.list_for_ref.return_value.json.return_value = {
        "check_runs": [
            {
                "name": settings.title,
                "app": {"id": settings.github_app_id},
                "output": {"summary": "my summary"},
            },
            {
                "name": "other check",
                "app": {"id": 456},
                "output": {"summary": "other summary"},
            },
        ]
    }

    result = cost._get_previous_check_run(g, webhook)
    assert result == "my summary"
    g.rest.checks.list_for_ref.assert_called_once_with(
        "myorg", "myrepo", "1234567890abcdef"
    )

    g.rest.checks.list_for_ref.return_value.json.return_value = {
        "check_runs": [
            {
                "name": "check",
                "app": {"id": 123},
                "output": {"summary": "my summary"},
            },
            {
                "name": "other check",
                "app": {"id": 456},
                "output": {"summary": "other summary"},
            },
        ]
    }

    result = cost._get_previous_check_run(g, webhook)
    assert result == ""
