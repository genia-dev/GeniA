import os

from kubernetes import client, config


class KubernetesClient:
    def __init__(self):
        if os.getenv("KUBERNETES_INCLUSTER_CONFIG"):
            config.load_incluster_config()
            self.client_config = client.Configuration()
            self.client_config.host = "https://kubernetes.default.svc:443"
            self.client_config.api_key = {
                "authorization": "Bearer " + open("/var/run/secrets/kubernetes.io/serviceaccount/token").read()
            }
            self.client_config.ssl_ca_cert = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
        else:
            self.client_config = config.load_kube_config()

    def get_batch_client(self):
        return client.BatchV1Api(client.ApiClient(self.client_config))

    def get_apps_client(self):
        return client.AppsV1Api(client.ApiClient(self.client_config))

    def get_core_api_client(self):
        return client.CoreV1Api(client.ApiClient(self.client_config))
