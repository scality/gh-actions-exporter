import logging
from gh_actions_exporter.types import WebHook
from gh_actions_exporter.metrics import Metrics

logger = logging.getLogger("runner_manager")


class WebhookManager(object):
    event: str
    payload: WebHook

    def __init__(self, payload: WebHook, event: str, metrics: Metrics):
        self.event = event
        self.payload = payload
        self.metrics = metrics

    def __call__(self, *args, **kwargs):
        # Check if we managed this event
        if self.event not in [method for method in dir(self) if method[:2] != "__"]:
            logger.error(f"Event {self.event} not managed")
        else:
            logger.info(f'Get event: {self.event}')
            getattr(self, self.event)()

    def workflow_run(self):
        self.metrics.handle_workflow_duration(self.payload)
        self.metrics.handle_workflow_status(self.payload)
        self.metrics.handle_workflow_rebuild(self.payload)

    def workflow_job(self):
        self.metrics.handle_job_status(self.payload)
        self.metrics.handle_job_duration(self.payload)

    def ping(self):
        logger.info('Ping from Github')
