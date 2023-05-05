import jinja2

from typing import Dict, List
from gh_actions_exporter.config import Relabel, RelabelType, Settings
from gh_actions_exporter.types import WebHook, JobCost
from gh_actions_exporter.tokenGenerator import TokenGenerator
from github import Github, Repository

class Cost(object):
    def __init__(self, settings: Settings):
        self.settings: Settings = settings 

    def _runner_type_job(self, job_request: dict) -> str:
        if 'self-hosted' in job_request["labels"]:
            return 'self-hosted'
        return 'github-hosted'

    def _get_job_cost(self, job_request: dict, flavor_label: str) -> float:
        cost_per_min: float = self.settings.job_costs.get(flavor_label, self.settings.default_cost)
        duration: float = (job_request["completed_at"].timestamp()
                    - job_request["started_at"].timestamp())

        if self._runner_type_job(job_request) == "github-hosted":
            return duration / 60 * self.settings.default_cost
        return duration / 60 * cost_per_min

    def _get_workflow_jobs_url(self, webhook: WebHook) -> str:
        return f"/repos/{webhook.repository.full_name}/actions/runs/{webhook.workflow_run.id}/jobs"

    def _get_workflow_jobs(self, webhook: WebHook, repository: Repository) -> dict:
        workflow_jobs: dict = repository._requester.requestJsonAndCheck("GET", self._get_workflow_jobs_url(webhook), {"Accept": "application/vnd.github.v3+json",})[1]
        return workflow_jobs

    def _generate_check_run_data(self, webhook: WebHook, total_cost: float, jobs_cost: List[JobCost], summary: str) -> dict:
        data: dict = {
            "summary": summary,
            "settings": {"summary": self.settings.summary},
            "workflow_run": {"name": webhook.workflow_run.name, "html_url": webhook.workflow_run.html_url},
            "jobs_cost": jobs_cost,
            "total_cost": total_cost,
        }
        return data

    def _get_previous_check_run(self, repository: Repository, webhook: WebHook) -> str:
        url: str = f"/repos/{webhook.repository.full_name}/commits/{webhook.workflow_run.head_sha}/check-runs"
        check_runs: dict = repository._requester.requestJsonAndCheck("GET", url, {"Accept": "application/vnd.github.v3+json",})[1]

        for check_run in check_runs["check_runs"]:
            if check_run["name"] == self.settings.title and check_run["app"]["id"] == self.settings.github_app_id:
                return check_run["output"]["summary"]
        return ""

    def _upload_check_run(self, summary: str, repository: Repository, webhook: WebHook) -> None:
        repository.create_check_run(
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
            repository: Repository = g.get_repo(webhook.repository.full_name)
            workflow_jobs: dict = self._get_workflow_jobs(webhook, repository)

            total_cost: float = 0.0
            jobs_cost: List[JobCost] = []
            for job in workflow_jobs["jobs"]:

                flavor_label: str = "flavor"
                for label in job["labels"]:
                    if label in self.settings.job_costs:
                        flavor_label = label
                        
                cost: float = self._get_job_cost(job, flavor_label)
                jobs_cost.append(JobCost(name=job["name"], cost=cost))
                total_cost += cost

            summary: str = self._get_previous_check_run(repository, webhook)

            data: dict = self._generate_check_run_data(webhook, total_cost, jobs_cost, summary)
            template = jinja2.Template(
                """{% if summary == "" %}
                {{ settings.summary }}
                {% endif %}
                ## [{{ workflow_run.name }}]({{ workflow_run.html_url }})
                {% for job_cost in jobs_cost %}* {{ job_cost.name }}: ${{ job_cost.cost }}
                {% endfor %}Total: ${{ total_cost }}"""
            )

            result: str = template.render(data)
            self._upload_check_run(result, repository, webhook)
