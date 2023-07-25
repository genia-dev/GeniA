import logging
from typing import Any
from kubernetes import client, stream

from genia.tools.kubernetes_client.kubernetes_clients import KubernetesClient


class KubernetesPod:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.api_client_core = KubernetesClient().get_core_api_client()

    def exec_command_in_pod(self, namespace, pod_name, command):
        resp = stream.stream(
            self.api_client_core.connect_get_namespaced_pod_exec,
            name=pod_name,
            namespace=namespace,
            command=command,
            stderr=True,
            stdin=True,
            stdout=True,
            tty=False,
        )

        return resp

    def delete_namespaced_pod(self, namespace, pod_name):
        resp = self.api_client_core.delete_namespaced_pod(
            name=pod_name,
            namespace=namespace,
            body=client.V1DeleteOptions(),
        )

    def list_namespaced_pod(self, namespace):
        resp = self.api_client_core.list_namespaced_pod(namespace=namespace)
        return [i.to_dict() for i in resp.items]

    def get_pod_logs_by_label(self, namespace, label):
        label_selector = "controller-uid={}".format(label)
        resp = self.api_client_core.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

        if resp.items:
            pod_name = resp.items[0].metadata.name
            return self.api_client_core.read_namespaced_pod_log(pod_name, namespace).split("\n")
        else:
            return []

    def create_pod_object(self, container_name, container_image):
        pod = client.V1Pod()
        pod.metadata = client.V1ObjectMeta(name=container_name)
        container = client.V1Container(name=container_name)
        container.image = container_image
        pod.spec = client.V1PodSpec(containers=[container])

        return pod

    def create_namespaced_pod(self, namespace, container_name, container_image):
        pod = self.create_pod_object(container_name, container_image)
        api_response = self.api_client_core.create_namespaced_pod(namespace=namespace, body=pod)
        self.logger.info(api_response)

    def patch_namespaced_pod(self, namespace, pod_name, body):
        patched_pod = self.api_client_core.patch_namespaced_pod(name=pod_name, namespace=namespace, body=body)

        patched_pod_info = {
            "name": patched_pod.metadata.name,
            "namespace": patched_pod.metadata.namespace,
            "labels": patched_pod.metadata.labels,
            "creationTimestamp": patched_pod.metadata.creation_timestamp,
            "phase": patched_pod.status.phase,
            "podIP": patched_pod.status.pod_ip,
            "hostIP": patched_pod.status.host_ip,
            "containers": [container.name for container in patched_pod.spec.containers],
        }

        return patched_pod_info

    def patch_namespaced_pod_image(self, namespace, pod_name, image):
        patch = {"spec": {"containers": [{"name": pod_name, "image": image}]}}

        return self.patch_namespaced_pod(namespace, pod_name, patch)

    def read_namespaced_pod(self, namespace, pod_name):
        pod = self.api_client_core.read_namespaced_pod(name=pod_name, namespace=namespace)

        pod_info = {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "labels": pod.metadata.labels,
            "creationTimestamp": pod.metadata.creation_timestamp,
            "phase": pod.status.phase,
            "podIP": pod.status.pod_ip,
            "hostIP": pod.status.host_ip,
            "containers": [{"name": container.name, "image": container.image} for container in pod.spec.containers],
        }

        return pod_info

    def read_namespaced_pod_resources(self, namespace, pod_name):
        pod = self.api_client_core.read_namespaced_pod(name=pod_name, namespace=namespace)

        containers_resources = []
        for container in pod.spec.containers:
            resources = {
                "name": container.name,
                "requests": container.resources.requests,
                "limits": container.resources.limits,
            }
            containers_resources.append(resources)

        return containers_resources

    def list_namespaced_pods_status(self, namespace, status_phase):
        field_selector = f"status.phase={status_phase}"
        resp = self.api_client_core.list_namespaced_pod(namespace=namespace, field_selector=field_selector)

        return [item.metadata.name for item in resp.items]

    def list_failed_pods_for_all_namespaces(self):
        field_selector = "status.phase=Failed"
        resp = self.api_client_core.list_pod_for_all_namespaces(field_selector=field_selector)

        return [item.metadata.name for item in resp.items]

    def get_pod_app_by_label(self, namespace, label_selector):
        return self.api_client_core.list_namespaced_pod(namespace, label_selector=label_selector)

    def get_service_owner(self, namespace, service, label_selector_serviceowner="serviceowner") -> Any:
        label_selector = f"app={service}"
        pods = self.get_pod_app_by_label(namespace, label_selector)
        return [pod.metadata.labels[label_selector_serviceowner] for pod in pods.items]
