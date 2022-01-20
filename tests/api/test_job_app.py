
import pytest

from fastapi.testclient import TestClient
from gh_actions_exporter.main import app


@pytest.fixture(autouse=True, scope='module')
def client():
    return TestClient(app)


@pytest.fixture
def workflow_run():
    webhook = {
        "workflow_run": {
            "id": 1468134741,
            "name": "test",
            "head_branch": "feature",
            "head_sha": "9dc4cd1747922994dc5249b866d3b1f37f09357d",
            "run_number": 42,
            "event": "push",
            "status": "queued",
            "conclusion": None,
            "workflow_id": 13826527,
            "created_at": "2021-11-16T17:52:47Z",
            "updated_at": "2021-11-16T17:53:32Z",
        },
        "repository": {
            "name": "repo",
            "full_name": "org/repo",
        }
    }
    return webhook, {'X-Github-Event': 'workflow_run'}


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
        },
        "repository": {
            "name": "test-runner-operator",
            "full_name": "scalanga-devl/test-runner-operator",
        }
    }
    return webhook, {'X-Github-Event': 'workflow_job'}


@pytest.fixture(autouse=True, scope='module')
def setup_function(client):
    client.delete('/clear')


def test_webhook_endpoint(client, workflow_run, workflow_job):
    response = client.post('/webhook', json=workflow_run[0], headers=workflow_run[1])
    assert response.status_code == 202


def test_webhook_in_progress(client, workflow_run, workflow_job):
    response = client.post('/webhook', json=workflow_run[0], headers=workflow_run[1])
    assert response.status_code == 202

    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    assert 'queued' in metrics.text

    response = client.post('/webhook', json=workflow_job[0], headers=workflow_job[1])
    assert response.status_code == 202

    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    assert 'in_progress' in metrics.text
