import pytest
from fastapi.testclient import TestClient
from gh_actions_exporter.main import app


@pytest.fixture(scope='function')
def client():
    client = TestClient(app)
    return client


@pytest.fixture(autouse=True)
def destroy_client(client):
    client.delete('/clear')


@pytest.fixture
def workflow_run():
    webhook = {
        "workflow_run": {
            "id": 1468134741,
            "name": "test",
            "head_branch": "feature",
            "head_sha": "9dc4cd1747922994dc5249b866d3b1f37f09357d",
            "run_number": 42,
            "run_attempt": 1,
            "event": "push",
            "status": "completed",
            "conclusion": "success",
            "workflow_id": 13826527,
            "created_at": "2021-11-16T17:52:47Z",
            "run_started_at": "2021-11-16T17:52:47Z",
            "updated_at": "2021-11-16T17:53:32Z",
        },
        "repository": {
            "name": "repo",
            "full_name": "org/repo",
            "visibility": "private",
        }
    }
    return webhook


@pytest.fixture
def workflow_job():
    webhook = {
        "workflow_job": {
            "id": 4355026428,
            "run_id": 1468134741,
            "run_url": "https://api.github.com/repos/-devl/fake",
            "run_attempt": 1,
            "node_id": "CR_kwDOFqdmms8AAAABA5Rt_A",
            "head_sha": "dfcc88973035bece77c0312f3f29e4e123e1f952",
            "url": "https://api.github.com/repos/scalanga-devl/fake",
            "html_url": "https://github.com/scalanga-devl/fake",
            "status": "in_progress",
            "conclusion": None,
            "started_at": "2021-11-29T14:46:57Z",
            "completed_at": None,
            "name": "greet (tata)",
            "steps": [
                {
                    "name": "Set up job",
                    "status": "in_progress",
                    "conclusion": None,
                    "number": 1,
                    "started_at": "2021-11-29T14:54:57Z",
                    "completed_at": None
                }
            ],
            "labels": ["github-hosted"]
        },
        "repository": {
            "name": "test-runner-operator",
            "full_name": "scalanga-devl/test-runner-operator",
            "visibility": "private",
        }
    }
    return webhook
