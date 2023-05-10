from functools import lru_cache

import pytest
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

from gh_actions_exporter.config import Relabel, Settings
from gh_actions_exporter.main import get_settings, metrics
from gh_actions_exporter.metrics import Metrics


@lru_cache()
def job_relabel_config():
    return Settings(
        job_relabelling=[
            Relabel(
                label="cloud", values=["mycloud"], type="name", default="github-hosted"
            ),
            Relabel(
                label="image",
                values=["ubuntu-latest"],
            ),
            Relabel(label="flavor", values=["large"], default="medium"),
        ],
    )


@lru_cache()
def default_settings():
    return Settings()


@lru_cache()
def default_metrics():
    return Metrics(default_settings())


@lru_cache()
def relabel_metrics():
    return Metrics(job_relabel_config())


def unregister_metrics():
    print(f"Unregistering {REGISTRY._collector_to_names}")
    for collector, names in tuple(REGISTRY._collector_to_names.items()):
        if any(name.startswith("github_actions") for name in names):
            REGISTRY.unregister(collector)


@pytest.fixture(scope="function")
def client(fastapp):
    unregister_metrics()
    default_settings.cache_clear()
    default_metrics.cache_clear()
    fastapp.dependency_overrides = {}
    fastapp.dependency_overrides[get_settings] = default_settings
    fastapp.dependency_overrides[metrics] = default_metrics
    client = TestClient(fastapp)
    return client


@pytest.fixture(scope="function")
def override_job_config(fastapp):
    unregister_metrics()
    fastapp.dependency_overrides = {}
    fastapp.dependency_overrides[get_settings] = job_relabel_config
    fastapp.dependency_overrides[metrics] = relabel_metrics


@pytest.fixture(scope="function", autouse=True)
def cleanup_metrics(client):
    client.delete("/clear")
