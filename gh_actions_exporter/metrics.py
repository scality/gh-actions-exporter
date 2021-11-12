import os
import datetime

from prometheus_client import (CONTENT_TYPE_LATEST, REGISTRY,
                               CollectorRegistry, generate_latest)
from prometheus_client.multiprocess import MultiProcessCollector
from fastapi.requests import Request
from fastapi.responses import Response
from gh_actions_exporter.types import WebHook
from prometheus_client import Enum, Gauge


def prometheus_metrics(request: Request) -> Response:
    if "prometheus_multiproc_dir" in os.environ:
        registry = CollectorRegistry()
        MultiProcessCollector(registry)
    else:
        registry = REGISTRY

    return Response(
        generate_latest(registry),
        headers={"Content-Type": CONTENT_TYPE_LATEST}
    )


class Metrics(object):

    def __init__(self):
        self.labelnames = [
            'name',
            'workflow_id',
            'head_sha',
            'head_branch',
            'status',
            'repo',
            'created_at',
            'updated_at'
        ]

        self.workflow_status = Enum(
            'github_actions_workflow_status', 'The state of a workflow',
            states=['success', 'in_progress', 'queued', 'skipped', 'failure'],
            labelnames=self.labelnames
        )
        self.workflow_duration = Gauge(
            'github_actions_workflow_duration_seconds',
            'The duration of a workflow in seconds',
            labelnames=self.labelnames
        )

    def set_time(self, webhook: WebHook, status: str):
        if webhook.workflow_run.conclusion:
            duration = (webhook.workflow_run.updated_at.timestamp()
                        - webhook.workflow_run.created_at.timestamp())
            self.workflow_duration.labels(
                name=webhook.workflow_run.name,
                workflow_id=webhook.workflow_run.workflow_id,
                head_sha=webhook.workflow_run.head_sha,
                head_branch=webhook.workflow_run.head_branch,
                status=status,
                repo=webhook.repository.full_name,
                created_at=webhook.workflow_run.created_at,
                updated_at=webhook.workflow_run.updated_at
            ).set(duration)

    def set_status(self, webhook: WebHook) -> str:
        if webhook.workflow_run.conclusion:
            status = webhook.workflow_run.conclusion
        else:
            status = webhook.workflow_run.status
        self.workflow_status.labels(
            name=webhook.workflow_run.name,
            workflow_id=webhook.workflow_run.workflow_id,
            head_sha=webhook.workflow_run.head_sha,
            head_branch=webhook.workflow_run.head_branch,
            status=webhook.workflow_run.status,
            repo=webhook.repository.full_name,
            created_at=webhook.workflow_run.created_at,
            updated_at=webhook.workflow_run.updated_at
        ).state(status)
        return status

    def cleaner(self):
        def test(elem):
            return (elem['status'] == 'completed'
                    and datetime.timedelta(minutes=5) < datetime.datetime.now() - elem['update_at'])

        for label in [elem for elem in self.workflow_status._samples() if test(elem)]:
            self.workflow_status.remove(*label)
            self.workflow_duration.remove(*label)
