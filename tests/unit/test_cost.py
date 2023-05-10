import datetime
from unittest.mock import MagicMock

import pytest

from gh_actions_exporter.config import Settings
from gh_actions_exporter.cost import Cost
from githubkit.rest import Job #, CheckRun, CheckRunPropOutput, Integration, ReposOwnerRepoCommitsRefCheckRunsGetResponse200


@pytest.fixture
def headers():
    headers = {"X-Github-Event": "workflow_run"}
    return headers


def test_runner_type_job():
    job_request = Job(
        id=1,
        run_id=1,
        run_url="1",
        run_attempt=1,
        node_id="1",
        head_sha="1",
        url="1",
        html_url="1",
        status="completed",
        started_at=datetime.datetime.now(),
        completed_at=datetime.datetime.now(),
        name="1",
        labels=["large", "jammy", "self-hosted"],
        conclusion="success",
        created_at="2021-11-16T17:52:47Z",
        check_run_url="url",
        runner_id=12,
        runner_name="name",
        runner_group_id=12,
        runner_group_name="name",
        workflow_name="name",
        head_branch="branch"
    )
    assert Cost(Settings())._runner_type_job(job_request) == "self-hosted"

    job_request = Job(
        id=1,
        run_id=1,
        run_url="1",
        run_attempt=1,
        node_id="1",
        head_sha="1",
        url="1",
        html_url="1",
        status="completed",
        started_at=datetime.datetime.now(),
        completed_at=datetime.datetime.now(),
        name="1",
        labels=["ubuntu-latest"],
        conclusion="success",
        created_at="2021-11-16T17:52:47Z",
        check_run_url="url",
        runner_id=12,
        runner_name="name",
        runner_group_id=12,
        runner_group_name="name",
        workflow_name="name",
        head_branch="branch"
    )
    assert Cost(Settings())._runner_type_job(job_request) == "github-hosted"


def test_get_job_cost():
    settings = Settings()

    job_request = Job(
        id=1,
        run_id=1,
        run_url="1",
        run_attempt=1,
        node_id="1",
        head_sha="1",
        url="1",
        html_url="1",
        status="completed",
        started_at="2021-11-16T17:52:47Z",
        completed_at="2021-11-16T17:58:47Z",
        name="1",
        labels=["self-hosted"],
        conclusion="success",
        created_at="2021-11-16T17:52:47Z",
        check_run_url="url",
        runner_id=12,
        runner_name="name",
        runner_group_id=12,
        runner_group_name="name",
        workflow_name="name",
        head_branch="branch"
    )
    assert Cost(settings)._get_job_cost(job_request, "large") == 0.096

    job_request = Job(
        id=1,
        run_id=1,
        run_url="1",
        run_attempt=1,
        node_id="1",
        head_sha="1",
        url="1",
        html_url="1",
        status="completed",
        started_at="2021-11-16T17:51:47Z",
        completed_at="2021-11-16T17:59:47Z",
        name="1",
        labels=["self-hosted"],
        conclusion="success",
        created_at="2021-11-16T17:52:47Z",
        check_run_url="url",
        runner_id=12,
        runner_name="name",
        runner_group_id=12,
        runner_group_name="name",
        workflow_name="name",
        head_branch="branch"
    )
    assert Cost(settings)._get_job_cost(job_request, "flavor") == 0.064

"""

def test_get_workflow_jobs():
    github = MagicMock()
    settings = Settings()
    webhook = MagicMock()
    webhook.organization.login = "myorg"
    webhook.repository.name = "myrepo"
    webhook.workflow_run.id = 123

    github.rest.checks.list_for_ref.return_value.json.return_value = {
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
    summary = cost._get_previous_check_run(github, webhook)
    assert summary == "Previous summary"

    github.rest.checks.list_for_ref.return_value.json.return_value = {
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

    summary = cost._get_previous_check_run(github, webhook)
    assert summary == ""
"""

"""
def test_get_previous_check_run():
    github = MagicMock()
    webhook = MagicMock()
    settings = Settings()
    cost = Cost(settings)

    webhook.organization.login = "myorg"
    webhook.repository.name = "myrepo"
    webhook.workflow_run.head_sha = "1234567890abcdef"

    check_run1 = CheckRun(
        id=1,
        head_sha="abc123",
        node_id="node_id_123",
        url="http://example.com/checks/1",
        status="completed",
        conclusion="success",
        output=CheckRunPropOutput(
            title="test",
            summary="my summary",
            text="test",
            annotations_count=1,
            annotations_url="url"
        ),
        name="my check",
        app=Integration(
            id=settings.github_app_id,
            name="My App"
        )
    )

    github.rest.checks.list_for_ref.return_value.json.return_value = ReposOwnerRepoCommitsRefCheckRunsGetResponse200(
            total_count=1,
            check_runs=[check_run1]
        )

    result = cost._get_previous_check_run(github, webhook)
    assert result == "my summary"
"""
