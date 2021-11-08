
import uvicorn

from fastapi import FastAPI

from gh_actions_exporter.metrics import prometheus_metrics, Metrics
from gh_actions_exporter.types import WebHook

app = FastAPI()
metrics = Metrics()

app.add_route('/metrics', prometheus_metrics)


@app.post("/webhook", status_code=202)
def webhook(webhook: WebHook):
    status = metrics.set_status(webhook)
    metrics.set_time(webhook, status)

    return "Accepted"


@app.get("/clear", status_code=200)
def clear():
    metrics.workflow_duration.clear()
    metrics.workflow_status.clear()
    return "Clear"


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run(
        "gh_actions_exporter.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
