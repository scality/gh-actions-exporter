import pytest


@pytest.fixture
def headers():
    headers = {"X-Github-Event": "workflow_job"}
    return headers


def test_webhook_job_endpoint(client, workflow_job, headers):
    response = client.post("/webhook", json=workflow_job, headers=headers)
    assert response.status_code == 202


def test_workflow_job_in_progress(client, workflow_job, headers):
    response = client.post("/webhook", json=workflow_job, headers=headers)
    assert response.status_code == 202

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    for line in metrics.text.split("\n"):
        if "inprogress_count_total{" in line:
            assert "1.0" in line
        if "start_duration_seconds_sum{" in line:
            assert "240.0" in line


def test_workflow_job_label_self_hosted(client, workflow_job, headers):
    workflow_job["workflow_job"]["labels"] = ["self-hosted", "ubuntu"]
    response = client.post("/webhook", json=workflow_job, headers=headers)
    assert response.status_code == 202

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "self-hosted" in metrics.text


def test_multiple_job_runs(client, workflow_job, headers):
    response = client.post("/webhook", json=workflow_job, headers=headers)
    assert response.status_code == 202

    workflow_job["workflow_job"]["conclusion"] = "success"
    workflow_job["workflow_job"]["completed_at"] = "2021-11-29T14:59:57Z"

    response = client.post("/webhook", json=workflow_job, headers=headers)
    assert response.status_code == 202

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert workflow_job["workflow_job"]["workflow_name"] in metrics.text

    for line in metrics.text.split("\n"):
        if "job_duration_seconds_sum{" in line:
            assert "780.0" in line
        if "job_total_count_total{" in line:
            assert "1.0" in line
        if "job_start_duration_seconds_sum{" in line:
            assert "240.0" in line


def test_job_relabel(override_job_config, client, workflow_job, headers):
    response = client.post("/webhook", json=workflow_job, headers=headers)
    metrics = client.get("/metrics")
    assert response.status_code == 202
    result = False
    # test default
    for line in metrics.text.split("\n"):
        if 'cloud="github-hosted"' in line:
            result = True
    assert result is True

    result = False
    # test name label relabeling
    workflow_job["workflow_job"]["runner_name"] = "runner-mycloud-1"
    response = client.post("/webhook", json=workflow_job, headers=headers)
    metrics = client.get("/metrics")
    for line in metrics.text.split("\n"):
        if 'cloud="mycloud"' in line:
            result = True
    assert result is True

    # test that multiple options are handled
    result = False
    for line in metrics.text.split("\n"):
        if 'image="ubuntu-latest"' in line:
            result = True
    assert result is True


def test_job_cost(client, workflow_job, headers):
    metrics = client.get("/metrics")
    for line in metrics.text.split("\n"):
        if "github_actions_job_cost_count_total{" in line:
            assert "0.0" in line

    workflow_job["workflow_job"]["conclusion"] = "success"
    workflow_job["workflow_job"]["completed_at"] = "2021-11-29T14:59:57Z"
    response = client.post("/webhook", json=workflow_job, headers=headers)
    assert response.status_code == 202

    metrics = client.get("/metrics")
    for line in metrics.text.split("\n"):
        if "github_actions_job_cost_count_total{" in line:
            assert "0.104" in line


def test_skipped_job(override_job_config, client, workflow_job, headers):
    workflow_job["workflow_job"]["runner_name"] = None
    workflow_job["workflow_job"]["status"] = "completed"
    workflow_job["workflow_job"]["conclusion"] = "skipped"
    workflow_job["workflow_job"]["completed_at"] = "2021-11-29T14:59:57Z"
    response = client.post("/webhook", json=workflow_job, headers=headers)
    assert response.status_code == 202
