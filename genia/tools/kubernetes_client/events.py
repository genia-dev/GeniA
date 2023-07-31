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

    def list_namespaced_pod_events(self, namespace, pod_name):
        events = self.api_client_events.list_namespaced_event(
            namespace, field_selector=f"involvedObject.name={pod_name}"
        )
        # return [event.to_dict() for event in events.items if event.type != "Normal"]
        return [event.message for event in events.items if event.type != "Normal"]
