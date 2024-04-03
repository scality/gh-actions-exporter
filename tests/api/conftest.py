import pytest
from fastapi.testclient import TestClient

from gh_actions_exporter.main import app


@pytest.fixture(scope="function")
def fastapp():
    fastapp = app
    fastapp.dependency_overrides = {}
    return fastapp


@pytest.fixture(scope="function")
def client(fastapp):
    client = TestClient(fastapp)
    return client


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
            "pull_requests": [
                {
                    "url": "https://api.github.com/repos/org/repo/pulls/555",
                    "id": 1805247,
                    "number": 555,
                    "head": {
                        "ref": "feature/my-feature",
                        "sha": "fc98b69edf5ac3f4789c210e758b1ee4b4396b9e",
                        "repo": {
                            "id": 395065315,
                            "url": "https://api.github.com/repos/org/repo",
                            "name": "repo",
                        },
                    },
                    "base": {
                        "ref": "master",
                        "sha": "966917b16d284edde596b0705a49f8c65ecf1c84",
                        "repo": {
                            "id": 395065125,
                            "url": "https://api.github.com/repos/org/repo",
                            "name": "repo",
                        },
                    },
                }
            ],
        },
        "repository": {
            "name": "repo",
            "full_name": "org/repo",
            "visibility": "private",
        },
    }
    return webhook


@pytest.fixture
def workflow_job():
    webhook = {
        "workflow_job": {
            "id": 4355026428,
            "run_id": 1468134741,
            "workflow_name": "test",
            "run_url": "https://api.github.com/repos/-devl/fake",
            "run_attempt": 1,
            "node_id": "CR_kwDOFqdmms8AAAABA5Rt_A",
            "head_sha": "dfcc88973035bece77c0312f3f29e4e123e1f952",
            "url": "https://api.github.com/repos/scalanga-devl/fake",
            "html_url": "https://github.com/scalanga-devl/fake",
            "status": "in_progress",
            "conclusion": None,
            "created_at": "2021-11-29T14:40:57Z",
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
