import os

from prometheus_client import (CONTENT_TYPE_LATEST, REGISTRY,
                               CollectorRegistry, generate_latest)
from prometheus_client.multiprocess import MultiProcessCollector
from fastapi.requests import Request
from fastapi.responses import Response
from gh_actions_exporter.types import WebHook
from prometheus_client import Counter, Histogram


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
        self.workflow_labelnames = [
            'repository',
            'workflow_name',
            'repository_visibility',
        ]
        self.job_labelnames = [
            'repository',
            'job_name',
            'repository_visibility',
            'runner_type'
        ]
        self.workflow_rebuild = Counter(
            'github_actions_workflow_rebuild_count', 'The number of workflow rebuild',
            labelnames=self.workflow_labelnames
        )
        self.workflow_duration = Histogram(
            'github_actions_workflow_duration_seconds',
            'The duration of a workflow in seconds',
            labelnames=self.workflow_labelnames
        )
        self.job_duration = Histogram(
            'github_actions_job_duration_seconds',
            'The duration of a job in seconds',
            labelnames=self.job_labelnames,
        )
        self.workflow_status_failure = Counter(
            'github_actions_workflow_failure_count',
            'Count the number of workflow failure',
            labelnames=self.workflow_labelnames
        )
        self.workflow_status_success = Counter(
            'github_actions_workflow_success_count',
            'Count the number of workflow success',
            labelnames=self.workflow_labelnames
        )
        self.workflow_status_cancelled = Counter(
            'github_actions_workflow_cancelled_count',
            'Count the number of workflow cancelled',
            labelnames=self.workflow_labelnames
        )
        self.workflow_status_inprogress = Counter(
            'github_actions_workflow_inprogress_count',
            'Count the number of workflow in progress',
            labelnames=self.workflow_labelnames
        )
        self.workflow_status_total = Counter(
            'github_actions_workflow_total_count',
            'Count the total number of workflows',
            labelnames=self.workflow_labelnames
        )
        self.job_status_failure = Counter(
            'github_actions_job_failure_count',
            'Count the number of job failure',
            labelnames=self.job_labelnames
        )
        self.job_status_success = Counter(
            'github_actions_job_success_count',
            'Count the number of job success',
            labelnames=self.job_labelnames
        )
        self.job_status_cancelled = Counter(
            'github_actions_job_cancelled_count',
            'Count the number of job cancelled',
            labelnames=self.job_labelnames
        )
        self.job_status_inprogress = Counter(
            'github_actions_job_inprogress_count',
            'Count the number of job in progress',
            labelnames=self.job_labelnames
        )
        self.job_status_queued = Counter(
            'github_actions_job_queued_count',
            'Count the number of job queued',
            labelnames=self.job_labelnames
        )
        self.job_status_total = Counter(
            'github_actions_job_total_count',
            'Count the total number of jobs',
            labelnames=self.job_labelnames
        )
        self.job_start_duration = Histogram(
            'github_actions_job_start_duration_seconds',
            'Time between when a job is requested and started',
            labelnames=self.job_labelnames
        )

    def workflow_labels(self, webhook: WebHook) -> dict:
        return dict(
            workflow_name=webhook.workflow_run.name,
            repository=webhook.repository.full_name,
            repository_visibility=webhook.repository.visibility,
        )

    def runner_type(self, webhook: WebHook) -> str:
        if 'self-hosted' in webhook.workflow_job.labels:
            return 'self-hosted'
        return 'github-hosted'

    def job_labels(self, webhook: WebHook) -> dict:
        labels = dict(
            runner_type=self.runner_type(webhook),
            job_name=webhook.workflow_job.name,
            repository_visibility=webhook.repository.visibility,
            repository=webhook.repository.full_name,
        )
        return labels

    def handle_workflow_rebuild(self, webhook: WebHook):
        # playing safe counting rebuild when workflow is complete
        # Ideally would like to find a trustworthy event to count
        # when workflows starts but as far as I can remember we keep
        # getting queued status multiple time for the same workflow
        # and not always in_progress
        labels = self.workflow_labels(webhook)
        if (webhook.workflow_run.conclusion
                and webhook.workflow_run.run_attempt > 1):
            self.workflow_rebuild.labels(**labels).inc()

    def handle_workflow_status(self, webhook: WebHook):
        labels = self.workflow_labels(webhook)
        if webhook.workflow_run.conclusion:
            if webhook.workflow_run.conclusion == 'success':
                self.workflow_status_success.labels(**labels).inc()
            elif webhook.workflow_run.conclusion == 'failure':
                self.workflow_status_failure.labels(**labels).inc()
            elif webhook.workflow_run.conclusion == 'cancelled':
                self.workflow_status_cancelled.labels(**labels).inc()
            self.workflow_status_total.labels(**labels).inc()
        # Hoping that the in_progress status will actually be sent and
        # only once
        elif webhook.workflow_run.status == "in_progress":
            self.workflow_status_inprogress.labels(**labels).inc()

    def handle_workflow_duration(self, webhook: WebHook):
        if webhook.workflow_run.conclusion:
            labels = self.workflow_labels(webhook)
            duration = (webhook.workflow_run.updated_at.timestamp()
                        - webhook.workflow_run.run_started_at.timestamp())
            self.workflow_duration.labels(**labels).observe(duration)

    def handle_job_status(self, webhook: WebHook):
        labels = self.job_labels(webhook)
        if webhook.workflow_job.conclusion == 'success':
            self.job_status_success.labels(**labels).inc()
        elif webhook.workflow_job.conclusion == 'failure':
            self.job_status_failure.labels(**labels).inc()
        elif webhook.workflow_job.conclusion == 'cancelled':
            self.job_status_cancelled.labels(**labels).inc()
        elif webhook.workflow_job.status == 'in_progress':
            self.job_status_inprogress.labels(**labels).inc()
            # For jobs the in progress is consistent and can be added to total count
            self.job_status_total.labels(**labels).inc()
        elif webhook.workflow_job.status == 'queued':
            self.job_status_queued.labels(**labels).inc()

    def handle_job_duration(self, webhook: WebHook):
        labels = self.job_labels(webhook)
        if webhook.workflow_job.conclusion:
            duration = (webhook.workflow_job.completed_at.timestamp()
                        - webhook.workflow_job.started_at.timestamp())
            self.job_duration.labels(**labels).observe(duration)
        elif webhook.workflow_job.status == "in_progress":
            duration = (webhook.workflow_job.steps[0].started_at.timestamp()
                        - webhook.workflow_job.started_at.timestamp())
            self.job_start_duration.labels(**labels).observe(duration)
