from genia.tools.kubernetes_client.kubernetes_clients import KubernetesClient


class KubernetesEvents:
    def __init__(self):
        self.api_client_events = KubernetesClient().get_core_api_client()

    def list_namespaced_events(self, namespace):
        events = self.api_client_events.list_namespaced_event(namespace)
        return [event.to_dict() for event in events.items]

    def list_events_for_all_namespaces(self):
        events = self.api_client_events.list_event_for_all_namespaces()
        return [event.to_dict() for event in events.items]
