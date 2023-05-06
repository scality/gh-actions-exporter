import pytest


@pytest.fixture
def headers():
    headers = {
        'X-Github-Event': 'workflow_run'
    }
    return headers


def test_workflow_run_endpoint(client, workflow_run, headers):
    response = client.post('/webhook', json=workflow_run, headers=headers)
    assert response.status_code == 202


def test_workflow_run_metrics(client, workflow_run, headers):
    upload = client.post('/webhook', json=workflow_run, headers=headers)
    assert upload.status_code == 202

    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    assert str(workflow_run['workflow_run']['name']) in metrics.text
    assert str(workflow_run['repository']['full_name']) in metrics.text


def test_multiple_workflow_runs(client, workflow_run, headers):
    workflow_run['workflow_run']['conclusion'] = None
    workflow_run['workflow_run']['status'] = 'in_progress'
    upload = client.post('/webhook', json=workflow_run, headers=headers)
    assert upload.status_code == 202

    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    assert 'inprogress' in metrics.text

    workflow_run['workflow_run']['conclusion'] = 'success'
    workflow_run['workflow_run']['status'] = 'completed'
    upload = client.post('/webhook', json=workflow_run, headers=headers)
    assert upload.status_code == 202

    metrics = client.get('/metrics')

    assert metrics.status_code == 200
    assert 'inprogress' in metrics.text
    assert 'success' in metrics.text


def test_rebuild(client, workflow_run, headers):
    workflow_run['workflow_run']['run_attempt'] = 2

    upload = client.post('/webhook', json=workflow_run, headers=headers)
    assert upload.status_code == 202
    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    for line in metrics.text.split('\n'):
        if 'workflow_rebuild_count_total{' in line:
            assert '1.0' in line
