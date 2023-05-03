import os
import requests

from prometheus_client import (CONTENT_TYPE_LATEST, REGISTRY,
                               CollectorRegistry, generate_latest)
from prometheus_client.multiprocess import MultiProcessCollector
from typing import Dict, List
from fastapi.requests import Request
from fastapi.responses import Response
from gh_actions_exporter.config import Relabel, RelabelType, Settings
from gh_actions_exporter.types import WebHook, WorkflowJob
from prometheus_client import Counter, Histogram
from gh_actions_exporter.jwtGenerator import JWTGenerator
from github import Github, Repository


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
    def __init__(self, settings: Settings):
        self.settings = settings
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
        for relabel in self.settings.job_relabelling:
            self.job_labelnames.append(relabel.label)

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
        # Metrics to sum the cost of a job
        self.job_cost = Counter(
            'github_actions_job_cost_count',
            'Cost of a job',
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

    def relabel_job_labels(self, relabel: Relabel, labels: List[str]) -> Dict[str, str or None]:
        result = {
            relabel.label: relabel.default
        }
        for label in relabel.values:
            if label in labels:
                result[relabel.label] = label
        return result

    def relabel_job_names(self, relabel: Relabel, job: WorkflowJob) -> dict:
        result = {
            relabel.label: relabel.default
        }
        if job.status == 'queued':
            result[relabel.label] = ""
        else:
            for label in relabel.values:
                if label in job.runner_name:
                    result[relabel.label] = label
        return result

    def job_labels(self, webhook: WebHook, settings: Settings) -> dict:
        labels = dict(
            runner_type=self.runner_type(webhook),
            job_name=webhook.workflow_job.name,
            repository_visibility=webhook.repository.visibility,
            repository=webhook.repository.full_name,
        )
        for relabel in settings.job_relabelling:
            if relabel.type == RelabelType.label:
                labels.update(self.relabel_job_labels(relabel, webhook.workflow_job.labels))
            elif relabel.type == RelabelType.name:
                labels.update(self.relabel_job_names(relabel, webhook.workflow_job))
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

    def handle_job_status(self, webhook: WebHook, settings: Settings):
        labels = self.job_labels(webhook, settings)
        if webhook.workflow_job.conclusion:
            if webhook.workflow_job.conclusion == 'success':
                self.job_status_success.labels(**labels).inc()
            elif webhook.workflow_job.conclusion == 'failure':
                self.job_status_failure.labels(**labels).inc()
            elif webhook.workflow_job.conclusion == 'cancelled':
                self.job_status_cancelled.labels(**labels).inc()
            self.job_status_total.labels(**labels).inc()
        elif webhook.workflow_job.status == 'in_progress':
            self.job_status_inprogress.labels(**labels).inc()
        elif webhook.workflow_job.status == 'queued':
            self.job_status_queued.labels(**labels).inc()

    def _get_job_duration(self, webhook: WebHook) -> float:
        if webhook.workflow_job.conclusion:
            return (webhook.workflow_job.completed_at.timestamp()
                    - webhook.workflow_job.started_at.timestamp())
        return 0

    def _get_workflow_duration(self, webhook: WebHook) -> float:
        if webhook.workflow_run.conclusion:
            return (webhook.workflow_run.completed_at.timestamp()
                    - webhook.workflow_run.started_at.timestamp())
        return 0

    def handle_job_duration(self, webhook: WebHook, settings: Settings):
        labels = self.job_labels(webhook, settings)
        if webhook.workflow_job.conclusion:
            duration = self._get_job_duration(webhook)
            self.job_duration.labels(**labels).observe(duration)
        elif webhook.workflow_job.status == "in_progress":
            duration = (webhook.workflow_job.steps[0].started_at.timestamp()
                        - webhook.workflow_job.started_at.timestamp())
            self.job_start_duration.labels(**labels).observe(duration)

    def handle_job_cost(self, webhook: WebHook, settings: Settings):
        labels = self.job_labels(webhook, settings)
        # look for the flavor label
        flavor = labels.get(settings.flavor_label, None)
        cost_per_min = settings.job_costs.get(flavor, settings.default_cost)
        if webhook.workflow_job.conclusion and cost_per_min:
            duration = self._get_job_duration(webhook)
            # Cost of runner is duration / 60 * cost_per_min
            self.job_cost.labels(**labels).inc(duration / 60 * cost_per_min)

    def relabel_job_names_dict(self, relabel: Relabel, job_request: dict) -> dict:
        result: dict = {
            relabel.label: relabel.default
        }
        if job_request["status"] == 'queued':
            result[relabel.label] = ""
        else:
            for label in relabel.values:
                if label in job_request["runner_name"]:
                    result[relabel.label] = label
        return result

    def runner_type_job(self, job_request: dict) -> str:
        if 'self-hosted' in job_request["labels"]:
            return 'self-hosted'
        return 'github-hosted'

    def job_request_labels(self, job_request: dict, webhook: WebHook, settings: Settings) -> dict:
        labels: dict = dict(
            runner_type=self.runner_type_job(job_request),
            job_name=job_request["name"],
            repository_visibility=webhook.workflow_run.repository.private,
            repository=webhook.workflow_run.repository.full_name,
        )
        for relabel in settings.job_relabelling:
            if relabel.type == RelabelType.label:
                labels.update(self.relabel_job_labels(relabel, job_request["labels"]))
            elif relabel.type == RelabelType.name:
                labels.update(self.relabel_job_names_dict(relabel, job_request))
        return labels

    def _get_job_cost(self, job_request: dict, webhook: WebHook, settings: Settings) -> float:
        labels: dict = self.job_request_labels(job_request, webhook, settings)
        flavor = labels.get(settings.flavor_label, None)
        cost_per_min: float = settings.job_costs.get(flavor, settings.default_cost)
        duration: float = (job_request["completed_at"].timestamp()
                    - job_request["started_at"].timestamp())

        return duration / 60 * cost_per_min

    def get_previous_check_run(self, headers: dict, webhook: WebHook):
        url: str = f'https://api.github.com/repos/{webhook.repository.full_name}/commits/{webhook.workflow_run.head_sha}/check-runs'
        response: dict = requests.get(url, headers=headers).json()

        for check_run in response["check_runs"]:
            if check_run["name"] == "Workflow Costs":
                return check_run["output"]["summary"]
        return ""

    def upload_check_run(self, summary: str, webhook: WebHook):
        repo: Repository = g.get_repo(webhook.repository.full_name)

        repo.create_check_run(
            name="Cost",
            head_sha=webhook.workflow_run.head_sha,
            status="completed",
            conclusion="success",
            output={
                "title": "Workflow Costs",
                "summary": summary
            }
        )

    def display_cost(self, webhook: WebHook, settings: Settings):
        if webhook.workflow_run.conclusion:
            jwt_generator: JWTGenerator = JWTGenerator()
            jwt_token: bytes = jwt_generator.generate_jwt()

            headers: dict = {
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {jwt_token}',
                'X-GitHub-Api-Version': '2022-11-28'
            }

            access_token_url: str = f'https://api.github.com/app/installations/{os.environ.get("INSTALLATION_ID", "")}/access_tokens'
            response: dict = requests.post(access_token_url, headers=headers)
            access_token: str = response.json()['token']

            url: str = f'https://api.github.com/repos/{webhook.repository.full_name}/actions/runs/{webhook.workflow_run.id}/jobs'
            response: dict = requests.get(url, headers=headers).json()

            total_cost: float = 0.0
            jobs_cost: dict = {}
            for job in response["jobs"]:
                cost: float = self._get_job_cost(job_request, webhook, request)
                jobs_cost[job["name"]] = cost
                total_cost += job_cost

            summary: str = get_previous_check_run(headers, webhook)

            if summary == "":
                summary = """Behind a CI run, there are servers running which cost money, so it
                    is important to be careful not to abuse this feature to avoid wasting money."""
            summary += "## [" + webhook.workflow_run.name + "](" + webhook.workflow_run.html_url + ")\n"
            for name, cost in jobs_cost.items():
                summary += "* " + name + ": $" + cost + "\n"
            summary += "Total: $" + total_cost + "\n"

            upload_check_run(summary, webhook)
