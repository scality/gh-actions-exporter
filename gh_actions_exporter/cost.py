import jinja2

from typing import Dict, List
from gh_actions_exporter.config import Relabel, RelabelType, Settings
from gh_actions_exporter.types import WebHook, JobCost
from gh_actions_exporter.tokenGenerator import TokenGenerator
from github import Github, Repository

class Cost(object):
    def __init__(self, settings: Settings):
        self.settings: Settings = settings 

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
    
    def relabel_job_labels(self, relabel: Relabel, labels: List[str]) -> Dict[str, str or None]:
        result: dict = {
            relabel.label: relabel.default
        }
        for label in relabel.values:
            if label in labels:
                result[relabel.label] = label
        return result

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

    def _get_job_cost(self, job_request: dict, webhook: WebHook) -> float:
        labels: dict = self.job_request_labels(job_request, webhook, self.settings)
        flavor = labels.get(self.settings.flavor_label, None)
        cost_per_min: float = self.settings.job_costs.get(flavor, self.settings.default_cost)
        duration: float = (job_request["completed_at"].timestamp()
                    - job_request["started_at"].timestamp())

        return duration / 60 * cost_per_min

    def get_previous_check_run(self, repository: Repository, webhook: WebHook) -> str:
        url: str = f"/repos/{webhook.repository.full_name}/commits/{webhook.workflow_run.head_sha}/check-runs"
        check_runs: dict = repository._requester.requestJsonAndCheck("GET", url, {"Accept": "application/vnd.github.v3+json",})[1]

        for check_run in check_runs["check_runs"]:
            if check_run["name"] == "self.settings.title" and check_run["app"]["id"] == self.settings.github_app_id:
                return check_run["output"]["summary"]
        return ""

    def upload_check_run(self, summary: str, webhook: WebHook, access_token: str) -> None:
        g: Github = Github(login_or_token=access_token)
        repo: Repository = g.get_repo(webhook.repository.full_name)

        repo.create_check_run(
            name="Cost",
            head_sha=webhook.workflow_run.head_sha,
            status="completed",
            conclusion="success",
            output={
                "title": self.settings.title,
                "summary": summary
            }
        )

    def display_cost(self, webhook: WebHook):
        if webhook.workflow_run.conclusion:
            token_generator: TokenGenerator = TokenGenerator(self.settings)
            access_token: str = token_generator.generate_token()
            
            g: Github = Github(access_token)
            repository: Repository = g.get_repo({webhook.repository.full_name})
            url: str = f"/repos/{webhook.repository.full_name}/actions/runs/{webhook.workflow_run.id}/jobs"
            workflow_jobs: dict = repository._requester.requestJsonAndCheck("GET", url, {"Accept": "application/vnd.github.v3+json",})[1]

            total_cost: float = 0.0
            jobs_cost: List[JobCost] = []
            for job in workflow_jobs["jobs"]:
                cost: float = self._get_job_cost(job, webhook)
                jobs_cost.append(JobCost(name=job["name"], cost=cost))
                total_cost += cost

            summary: str = self.get_previous_check_run(repository, webhook)

            template = jinja2.Template(
                """{% if summary == "" %}
                {{ settings.summary }}
                {% endif %}
                ## [{{ workflow_run.name }}]({{ workflow_run.html_url }})
                {% for job_cost in jobs_cost %}* {{ job_cost.name }}: ${{ job_cost.cost }}
                {% endfor %}Total: ${{ total_cost }}"""
            )

            data: dict = {
                "summary": summary,
                "settings": {"summary": self.settings.summary},
                "workflow_run": {"name": webhook.workflow_run.name, "html_url": webhook.workflow_run.html_url},
                "jobs_cost": jobs_cost,
                "total_cost": total_cost,
            }

            result: str = template.render(data)
            self.upload_check_run(result, webhook, access_token)