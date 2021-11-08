import os

from prometheus_client import (CONTENT_TYPE_LATEST, REGISTRY,
                               CollectorRegistry, generate_latest)
from prometheus_client.multiprocess import MultiProcessCollector
from fastapi.requests import Request
from fastapi.responses import Response
from gh_actions_exporter.types import WebHook
from prometheus_client import Enum, Summary


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
            'started_at',
            'completed_at'
        ]

        self.workflow_status = Enum(
            'github_actions_workflow_status', 'The state of a workflow',
            states=['success', 'in_progress', 'queued', 'skipped', 'failure'],
            labelnames=self.labelnames
        )
        self.workflow_duration = Summary(
            'github_actions_workflow_duration', 'The duration of a workflow',
            labelnames=self.labelnames
        )

    def set_time(self, webhook: WebHook, status: str):
        if webhook.check_suite.conclusion:
            duration = (webhook.check_suite.completed_at.timestamp()
                        - webhook.check_suite.started_at.timestamp())
            self.workflow_duration.labels(
                name=webhook.check_suite.name,
                workflow_id=webhook.check_suite.id,
                head_sha=webhook.check_suite.head_sha,
                head_branch=webhook.check_suite.head_branch,
                status=status,
                repo=webhook.repository.full_name,
                started_at=webhook.check_suite.started_at,
                completed_at=webhook.check_suite.completed_at
            ).observe(duration)

    def set_status(self, webhook: WebHook) -> str:
        if webhook.check_suite.conclusion:
            status = webhook.check_suite.conclusion
        else:
            status = webhook.check_suite.status
        self.workflow_status.labels(
            name=webhook.check_suite.name,
            workflow_id=webhook.check_suite.id,
            head_sha=webhook.check_suite.head_sha,
            head_branch=webhook.check_suite.head_branch,
            status=webhook.check_suite.status,
            repo=webhook.repository.full_name,
            started_at=webhook.check_suite.started_at,
            completed_at=webhook.check_suite.completed_at
        ).state(status)
        return status
