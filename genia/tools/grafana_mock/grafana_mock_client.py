import logging


class GraphanaMockClient:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.logger.info("GraphanaMockClient init")

    def get_service_metrics(self, service_name):
        self.logger.info("GraphanaMockClient get_service_metrics")
        return {"message": "bar"}

    def get_service_metric_data(self, service_name, metric_name):
        self.logger.info("GraphanaMockClient get_service_metric_data")
        return {"message": "foo"}
