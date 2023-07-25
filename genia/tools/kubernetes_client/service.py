from genia.tools.kubernetes_client.kubernetes_clients import KubernetesClient


class KubernetesService:
    def __init__(self):
        self.api_client_secret = KubernetesClient().get_core_api_client()

    def list_services(self, namespace):
        api_response = self.api_client_secret.list_namespaced_service(namespace)
        services = []
        for item in api_response.items:
            service = {
                "name": item.metadata.name,
                "namespace": item.metadata.namespace,
                "type": item.spec.type,
                "cluster_ip": item.spec.cluster_ip,
                "external_ip": item.spec.external_i_ps,
                "ports": [f"{port.protocol}/{port.port}" for port in item.spec.ports],
            }
            services.append(service)
        return services

    def get_service(self, namespace, service_name):
        api_response = self.api_client_secret.read_namespaced_service(service_name, namespace)
        service = {
            "name": api_response.metadata.name,
            "namespace": api_response.metadata.namespace,
            "type": api_response.spec.type,
            "cluster_ip": api_response.spec.cluster_ip,
            "external_ip": api_response.spec.external_i_ps,
            "ports": [f"{port.protocol}/{port.port}" for port in api_response.spec.ports],
        }
        return service
