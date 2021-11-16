
import pytest

from fastapi.testclient import TestClient
from gh_actions_exporter.main import app
from time import sleep


@pytest.fixture(autouse=True, scope='module')
def client():
    return TestClient(app)


@pytest.fixture
def webhook():
    webhook = {
        "workflow_run": {
            "id": 1468134741,
            "name": "test",
            "head_branch": "feature",
            "head_sha": "9dc4cd1747922994dc5249b866d3b1f37f09357d",
            "run_number": 42,
            "event": "push",
            "status": "completed",
            "conclusion": "success",
            "workflow_id": 13826527,
            "created_at": "2021-11-16T17:52:47Z",
            "updated_at": "2021-11-16T17:53:32Z",
        },
        "repository": {
            "name": "repo",
            "full_name": "org/repo",
        }
    }
    return webhook


@pytest.fixture
def headers():
    headers = {
        'X-Github-Event': 'workflow_run'
    }
    return headers


@pytest.fixture(autouse=True, scope='module')
def setup_function(client):
    client.delete('/clear')


def test_webhook_endpoint(client, webhook, headers):
    response = client.post('/webhook', json=webhook, headers=headers)
    assert response.status_code == 202


def test_metrics_endpoint(client, webhook, headers):
    upload = client.post('/webhook', json=webhook, headers=headers)
    assert upload.status_code == 202

    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    assert str(webhook['workflow_run']['workflow_id']) in metrics.text


def test_metrics_transition_no_duplicate(client, webhook, headers):
    webhook['workflow_run']['conclusion'] = None
    webhook['workflow_run']['status'] = 'queued'
    upload = client.post('/webhook', json=webhook, headers=headers)
    assert upload.status_code == 202

    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    assert 'queued' in metrics.text

    webhook['workflow_run']['conclusion'] = 'success'
    webhook['workflow_run']['status'] = 'completed'
    upload = client.post('/webhook', json=webhook, headers=headers)
    assert upload.status_code == 202

    metrics = client.get('/metrics')

    assert metrics.status_code == 200
    assert metrics.text.count('queued') == 1
    assert 'success' in metrics.text


def test_metrics_clean(client, webhook, headers):
    upload = client.post('/webhook', json=webhook, headers=headers)
    assert upload.status_code == 202

    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    assert webhook['workflow_run']['status'] in metrics.text

    delete = client.delete('/status/removes')
    assert delete.status_code == 200

    # Metrics are cached by the collector
    # trying multiple time to ensure we are not
    # hitting the cache and fail by mistake
    for i in range(10, 1):
        try:
            metrics = client.get('/metrics')
            assert str(webhook['workflow_run']['workflow_id']) not in metrics.text
        except AssertionError as exp:
            if i == 10:
                raise AssertionError(exp)
            else:
                sleep(i)
                continue


def test_metrics_clear(client, webhook, headers):
    upload = client.post('/webhook', json=webhook, headers=headers)
    assert upload.status_code == 202

    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    assert webhook['workflow_run']['status'] in metrics.text

    metrics = client.delete('/clear')
    assert metrics.status_code == 200
    assert 'github_actions_workflow_status' not in metrics.text


def test_unsupported_events(client, webhook, headers):
    """Ensure we don't crash on other webhook events"""
    headers['X-GitHub-Event'] = 'push'
    response = client.post('/webhook', json=webhook, headers=headers)

    response.status_code == 202
