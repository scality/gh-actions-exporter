import pytest


@pytest.fixture
def headers():
    headers = {
        'X-Github-Event': 'workflow_job'
    }
    return headers


def test_webhook_job_endpoint(client, workflow_job, headers):
    response = client.post('/webhook', json=workflow_job, headers=headers)
    assert response.status_code == 202


def test_workflow_job_in_progress(client, workflow_job, headers):
    response = client.post('/webhook', json=workflow_job, headers=headers)
    assert response.status_code == 202

    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    for line in metrics.text.split('\n'):
        if 'inprogress_count_total{' in line:
            assert "1.0" in line
        if 'start_duration_seconds_sum{' in line:
            assert '480.0' in line


def test_workflow_job_label_self_hosted(client, workflow_job, headers):
    workflow_job['workflow_job']['labels'] = ['self-hosted', 'ubuntu']
    response = client.post('/webhook', json=workflow_job, headers=headers)
    assert response.status_code == 202

    metrics = client.get('/metrics')
    assert metrics.status_code == 200
    assert 'self-hosted' in metrics.text


def test_multiple_job_runs(client, workflow_job, headers):
    response = client.post('/webhook', json=workflow_job, headers=headers)
    assert response.status_code == 202

    workflow_job['workflow_job']['conclusion'] = 'success'
    workflow_job['workflow_job']['completed_at'] = '2021-11-29T14:59:57Z'

    response = client.post('/webhook', json=workflow_job, headers=headers)
    assert response.status_code == 202

    metrics = client.get('/metrics')
    assert metrics.status_code == 200

    for line in metrics.text.split('\n'):
        if 'job_duration_seconds_sum{' in line:
            assert '780.0' in line
        if 'job_total_count_total{' in line:
            assert '1.0' in line
