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
            'run_number',
            'created_at',
            'finished_at'
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
                run_number=webhook.workflow_run.run_number,
                created_at=webhook.workflow_run.created_at,
                finished_at=webhook.workflow_run.updated_at
            ).set(duration)

    def set_status(self, webhook: WebHook) -> str:
        if webhook.workflow_run.conclusion:
            status = webhook.workflow_run.conclusion
            finished_at = webhook.workflow_run.updated_at
            try:
                # Remove old status to avoid duplicates
                self.workflow_status.remove(
                    webhook.workflow_run.name,
                    webhook.workflow_run.workflow_id,
                    webhook.workflow_run.head_sha,
                    webhook.workflow_run.head_branch,
                    # Previous status is queued
                    "queued",
                    webhook.repository.full_name,
                    webhook.workflow_run.run_number,
                    str(webhook.workflow_run.created_at),
                    # finished_at set as none
                    None
                )
            except KeyError:
                print('metric does not exist in the registry')
                pass
        else:
            status = webhook.workflow_run.status
            finished_at = None
        self.workflow_status.labels(
            name=webhook.workflow_run.name,
            workflow_id=webhook.workflow_run.workflow_id,
            head_sha=webhook.workflow_run.head_sha,
            head_branch=webhook.workflow_run.head_branch,
            status=webhook.workflow_run.status,
            repo=webhook.repository.full_name,
            run_number=webhook.workflow_run.run_number,
            created_at=webhook.workflow_run.created_at,
            finished_at=finished_at
        ).state(status)
        return status

    def remove_completed_workflow(self):
        """Stop exposing workflows that are completed."""
        def can_delete_sample(sample):
            """Returns True when sample can be deleted."""
            labels = sample[1]
            value = sample[2]
            finished_at = datetime.datetime.fromisoformat(labels['finished_at'])
            now = datetime.datetime.now(datetime.timezone.utc)
            # Only get metrics where value is 1 as it reflects the current state
            return (labels['status'] == 'completed' and value == 1
                    and datetime.timedelta(minutes=5) < now - finished_at)

        for label in [sample[1] for sample in self.workflow_status._samples()
                      if can_delete_sample(sample)]:
            self.workflow_status.remove(
                label['name'],
                label['workflow_id'],
                label['head_sha'],
                label['head_branch'],
                label['run_number'],
                label['status'],
                label['repo'],
                label['created_at'],
                label['finished_at'],
            )
            self.workflow_duration.remove(
                label['name'],
                label['workflow_id'],
                label['head_sha'],
                label['head_branch'],
                label['run_number'],
                # status in workflow duration is actually set as the state on workflow_status
                label['github_actions_workflow_status'],
                label['repo'],
                label['created_at'],
                label['finished_at'],
            )
