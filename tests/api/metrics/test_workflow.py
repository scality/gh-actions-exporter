import pytest


@pytest.fixture
def headers():
    headers = {"X-Github-Event": "workflow_run"}
    return headers


def test_workflow_run_endpoint(client, workflow_run, headers):
    response = client.post("/webhook", json=workflow_run, headers=headers)
    assert response.status_code == 202


def test_workflow_run_metrics(client, workflow_run, headers):
    upload = client.post("/webhook", json=workflow_run, headers=headers)
    assert upload.status_code == 202

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert workflow_run["workflow_run"]["name"] in metrics.text
    assert workflow_run["repository"]["full_name"] in metrics.text


def test_multiple_workflow_runs(client, workflow_run, headers):
    workflow_run["workflow_run"]["conclusion"] = None
    workflow_run["workflow_run"]["status"] = "in_progress"
    upload = client.post("/webhook", json=workflow_run, headers=headers)
    assert upload.status_code == 202

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "inprogress" in metrics.text

    workflow_run["workflow_run"]["conclusion"] = "success"
    workflow_run["workflow_run"]["status"] = "completed"
    upload = client.post("/webhook", json=workflow_run, headers=headers)
    assert upload.status_code == 202

    metrics = client.get("/metrics")

    assert metrics.status_code == 200
    assert "inprogress" in metrics.text
    assert "success" in metrics.text


def test_rebuild(client, workflow_run, headers):
    workflow_run["workflow_run"]["run_attempt"] = 2

    upload = client.post("/webhook", json=workflow_run, headers=headers)
    assert upload.status_code == 202
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    for line in metrics.text.split("\n"):
        if "workflow_rebuild_count_total{" in line:
            assert "1.0" in line


def test_branch_label(client, workflow_run, headers):
    # Ensure a feature branch is not indexed
    upload = client.post("/webhook", json=workflow_run, headers=headers)
    assert upload.status_code == 202

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert 'branch="feature"' not in metrics.text
    assert 'branch="dev"' in metrics.text

    # Index a push event with a branch label
    workflow_run["workflow_run"]["head_branch"] = "main"
    upload = client.post("/webhook", json=workflow_run, headers=headers)
    assert upload.status_code == 202

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert 'branch="main"' in metrics.text

    # Index a branch with a fnmatch pattern configured
    workflow_run["workflow_run"]["head_branch"] = "development/1.2"
    upload = client.post("/webhook", json=workflow_run, headers=headers)
    assert upload.status_code == 202

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert 'branch="development/1.2"' in metrics.text

    # Index the base branch of a pull request
    workflow_run["workflow_run"]["event"] = "pull_request"
    upload = client.post("/webhook", json=workflow_run, headers=headers)
    assert upload.status_code == 202

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert 'branch="master"' in metrics.text
