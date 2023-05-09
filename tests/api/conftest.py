
import pytest
from gh_actions_exporter.main import app, get_settings, metrics, github_client
from functools import lru_cache
from gh_actions_exporter.config import Settings
from gh_actions_exporter.metrics import Metrics
from gh_actions_exporter.githubClient import GithubClient

from fastapi.testclient import TestClient

@lru_cache()
def default_settings():
    # Setting up the required values only
    return Settings(
        github_app_id=42,
        github_app_installation_id=42,
        github_app_private_key="private key"
    )

@lru_cache()
def default_metrics():
    return Metrics(default_settings())


@lru_cache()
def default_github_client():
    return GithubClient(default_settings())


@pytest.fixture(scope="function", autouse=True)
def fastapp():

    app.dependency_overrides[get_settings] = default_settings
    app.dependency_overrides[metrics] = default_metrics
    app.dependency_overrides[github_client] = default_github_client
    fastapp = app
    return fastapp

@pytest.fixture(scope="function")
def client(fastapp):
    client = TestClient(fastapp)
    return client


@pytest.fixture(scope="function", autouse=True)
def destroy_client(client):
    client.delete("/clear")


@pytest.fixture
def workflow_run():
    webhook = {
        "workflow_run": {
            "id": 4863423668,
            "name": "test",
            "head_branch": "feature",
            "head_sha": "546c86cb55726fd1e647b9a886c0c5ee63ca0718",
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
            "name": "runners-test",
            "full_name": "scalanga-devl/runners-test",
            "visibility": "private",
        },
        "organization": {"login": "scalanga-devl"},
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
            "runner_name": "GitHub Actions 3",
            "steps": [
                {
                    "name": "Set up job",
                    "status": "completed",
                    "conclusion": "success",
                    "number": 1,
                    "started_at": "2021-11-29T14:50:57Z",
                    "completed_at": None,
                }
            ],
            "labels": ["ubuntu-latest"],
        },
        "repository": {
            "name": "test-runner-operator",
            "full_name": "scalanga-devl/test-runner-operator",
            "visibility": "private",
        },
    }
    return webhook
