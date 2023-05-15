from githubkit.webhooks import WorkflowJob

from gh_actions_exporter.config import Settings


class Cost(object):
    def __init__(self, settings: Settings):
        self.settings: Settings = settings

    def get_job_cost(self, workflow_job: WorkflowJob, flavor_label: str) -> float:
        cost_per_min: float = self.settings.job_costs.get(
            flavor_label, self.settings.default_cost
        )
        duration: int = int(workflow_job.completed_at.timestamp()) - int(
            workflow_job.started_at.timestamp()
        )

        return duration / 60 * cost_per_min
