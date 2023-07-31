from genia.tools.kubernetes_client.kubernetes_clients import KubernetesClient
from genia.tools.kubernetes_client.deployment import KubernetesDeployment
import logging


class KubernetesGlobal:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.api_client_core = KubernetesClient().get_core_api_client()
        self.api_client_apps = KubernetesClient().get_apps_client()

    def kubernetes_get_service_errors(self, service, namespace="default"):
        # TODO grab all k8s entities for that logic
        self.logger.debug(f"get service errors for namespace:{namespace}")
        deployment_api = KubernetesDeployment()
        return deployment_api.get_pods_errors_events_by_deployment(service)
