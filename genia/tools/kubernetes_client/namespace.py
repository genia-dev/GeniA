import logging

from genia.tools.kubernetes_client.kubernetes_clients import KubernetesClient
from genia.tools.kubernetes_client.cronjob import KubernetesCronJob
from kubernetes.client import V1Namespace


class KubernetesNamespace:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.api_client_core = KubernetesClient().get_core_api_client()
        self.api_client_cronjob = KubernetesCronJob()

    def list_namespaces(self):
        api_client = self.api_client_core
        api_response = api_client.list_namespace()
        return [item.metadata.name for item in api_response.items if item.status.phase == "Active"]

    def create_namespace(self, namespace):
        api_client = self.api_client_core
        namespace_body = V1Namespace(
            metadata={
                "name": namespace,
            }
        )
        api_response = api_client.create_namespace(body=namespace_body)
        self.logger.info(api_response)

    def delete_namespace(self, namespace):
        api_client = self.api_client_core
        api_response = api_client.delete_namespace(name=namespace)
        self.logger.info(api_response)

    def get_namespace(self, namespace):
        api_client = self.api_client_core
        namespace = api_client.read_namespace(name=namespace)
        self.logger.info(namespace)

        name = namespace.metadata.name
        status = namespace.status.phase

        return {
            "name": name,
            "status": status,
        }
