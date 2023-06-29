from functools import lru_cache

import uvicorn
from fastapi import Depends, FastAPI, Request
from githubkit import AppInstallationAuthStrategy, GitHub
from prometheus_client import make_asgi_app

from gh_actions_exporter.config import Settings
from gh_actions_exporter.metrics import Metrics
from gh_actions_exporter.types import WebHook
from gh_actions_exporter.Webhook import WebhookManager


@lru_cache()
def get_settings() -> Settings:
    return Settings()


@lru_cache()
def metrics() -> Metrics:
    return Metrics(get_settings())


@lru_cache()
def github_client() -> GitHub or None:
    settings: Settings = get_settings()
    if settings.check_runs_enabled:
        return GitHub(
            AppInstallationAuthStrategy(
                settings.github_app_id,
                settings.github_app_private_key.get_secret_value(),
                settings.github_app_installation_id,
            )
        )
    return None


app = FastAPI()

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/", status_code=200)
def index():
    return "OK"


@app.post("/webhook", status_code=202)
async def webhook(
    webhook: WebHook,
    request: Request,
    settings: Settings = Depends(get_settings),
    metrics: Metrics = Depends(metrics),
    github_client: GitHub = Depends(github_client),
):
    WebhookManager(
        payload=webhook,
        event=request.headers["X-Github-Event"],
        metrics=metrics,
        settings=settings,
        github_client=github_client,
    )()
    return "Accepted"


@app.delete("/clear", status_code=200)
async def clear(metrics: Metrics = Depends(metrics)):
    metrics.workflow_rebuild.clear()
    metrics.workflow_duration.clear()
    metrics.job_duration.clear()
    metrics.workflow_status_failure.clear()
    metrics.workflow_status_success.clear()
    metrics.workflow_status_cancelled.clear()
    metrics.workflow_status_inprogress.clear()
    metrics.workflow_status_total.clear()
    metrics.job_status_failure.clear()
    metrics.job_status_success.clear()
    metrics.job_status_cancelled.clear()
    metrics.job_status_inprogress.clear()
    metrics.job_status_queued.clear()
    metrics.job_status_total.clear()
    metrics.job_start_duration.clear()
    metrics.job_cost.clear()
    metrics.workflow_cost.clear()


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("gh_actions_exporter.main:app", host="0.0.0.0", port=8000, reload=True)
