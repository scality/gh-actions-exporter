from functools import lru_cache
import pytest
from fastapi.testclient import TestClient
from gh_actions_exporter.main import app, get_settings, metrics
from gh_actions_exporter.metrics import Metrics
from gh_actions_exporter.config import Relabel, Settings
from prometheus_client import REGISTRY


@lru_cache()
def job_relabel_config():
    return Settings(job_relabelling=[
        Relabel(
            label="cloud",
            values=[
                "mycloud"
            ],
            type="name",
            default="github-hosted"
        ),
        Relabel(
            label="image",
            values=[
                "ubuntu-latest"
            ],
        )
    ])


@lru_cache()
def relabel_metrics():
    return Metrics(job_relabel_config())


def unregister_metrics():
    print(f'Unregistering {REGISTRY._collector_to_names}')
    for collector, names in tuple(REGISTRY._collector_to_names.items()):
        if any(name.startswith('github_actions') for name in names):
            REGISTRY.unregister(collector)


@pytest.fixture(scope='function')
def override_job_config(fastapp):
    unregister_metrics()
    fastapp.dependency_overrides[get_settings] = job_relabel_config
    fastapp.dependency_overrides[metrics] = relabel_metrics


@pytest.fixture(scope='function', autouse=True)
def fastapp():
    fastapp = app
    return fastapp


@pytest.fixture(scope='function')
def client(fastapp):
    client = TestClient(fastapp)
    return client


@pytest.fixture(scope='function', autouse=True)
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
            "runner_name": "GitHub Actions 3",
            "steps": [
                {
                    "name": "Set up job",
                    "status": "completed",
                    "conclusion": "success",
                    "number": 1,
                    "started_at": "2021-11-29T14:50:57Z",
                    "completed_at": None
                }
            ],
            "labels": ["ubuntu-latest"]
        },
        "repository": {
            "name": "test-runner-operator",
            "full_name": "scalanga-devl/test-runner-operator",
            "visibility": "private",
        }
    }
    return webhook
