from datetime import datetime, timedelta

import pytest
from githubkit.webhooks import WorkflowJob

from gh_actions_exporter.config import Settings


@pytest.fixture
def workflow_job():
    return WorkflowJob(
        id=123,
        run_id=456789,
        run_attempt=1,
        run_url="https://github.com/user/repo/actions/runs/123",
        head_sha="a1b2c3d4e5f6g7h8i9j0",
        node_id="MDg6Q29tbWl0MTIzNDU2Nzg5OnNhbXBsZQ==",
        name="Job 1",
        check_run_url="https://api.github.com/repos/user/repo/check-runs/123",
        html_url="https://github.com/user/repo/actions/runs/123",
        url="https://api.github.com/repos/user/repo/actions/jobs/123",
        status="queued",
        steps=[],
        conclusion=None,
        labels=["label1", "label2"],
        runner_id=None,
        runner_name=None,
        runner_group_id=None,
        runner_group_name=None,
        started_at=datetime(2021, 1, 1, 0, 0),
        completed_at=datetime(2021, 1, 1, 0, 0) + timedelta(minutes=10),
        workflow_name=None,
        head_branch=None,
        created_at=datetime.now(),
    )


@pytest.fixture
def settings():
    return Settings()
