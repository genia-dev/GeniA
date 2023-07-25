from genia.tools.kubernetes_client.kubernetes_clients import KubernetesClient


class KubernetesSecret:
    def __init__(self):
        self.api_client_secret = KubernetesClient().get_core_api_client()

    def list_namespaced_secret(self, namespace):
        secrets = self.api_client_secret.list_namespaced_secret(namespace)
        [secret for secret in secrets.items]

    def check_secret_exists(self, secret_name, namespace):
        self.api_client_secret.read_namespaced_secret(secret_name, namespace)
        return True
