import uvicorn

from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every

from gh_actions_exporter.metrics import prometheus_metrics, Metrics
from gh_actions_exporter.types import WebHook
from gh_actions_exporter.Webhook import WebhookManager

app = FastAPI()
metrics = Metrics()

app.add_route('/metrics', prometheus_metrics)


@app.on_event("startup")
@repeat_every(seconds=10)
def clean_completed_workflow() -> None:
    metrics.remove_completed_workflow()


@app.get("/", status_code=200)
def index():
    return "OK"


@app.post("/webhook", status_code=202)
async def webhook(webhook: WebHook, request: Request):
    WebhookManager(payload=webhook, event=request.headers['X-Github-Event'], metrics=metrics)()
    return "Accepted"


@app.get("/status")
async def list_status():
    return [elem for elem in metrics.workflow_status._samples()]


@app.delete("/status/removes")
async def remove_old_status():
    await clean_completed_workflow()
    return "Accepted"


@app.delete("/clear", status_code=200)
async def clear():
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
