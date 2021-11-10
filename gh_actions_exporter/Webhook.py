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
            logger.info(f"Event {self.event} not managed")
        else:
            logger.info(f'Get event: {self.event}')
            getattr(self, self.event)(self.payload)

    def workflow_run(self, payload):
        status = self.metrics.set_status(self.payload)
        self.metrics.set_time(self.payload, status)

    def workflow_job(self, payload):
        pass

    def ping(self, payload):
        logger.info('Ping from Github')
