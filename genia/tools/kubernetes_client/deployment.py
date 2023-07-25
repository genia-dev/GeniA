import time
import threading
from genia.tools.kubernetes_client.kubernetes_clients import KubernetesClient

from kubernetes import client
import logging
from tenacity import (
    retry,
    retry_if_exception_type,
    wait_random_exponential,
    stop_after_attempt,
)

from kubernetes.client.exceptions import ApiException


class DeploymentUpdateConflictError(ApiException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = "Unable to update the deployment due to a conflict."


class KubernetesDeployment:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.api_client_core = KubernetesClient().get_core_api_client()
        self.api_client_apps = KubernetesClient().get_apps_client()

    def describe_deployment(self, namespace, deployment_name):
        deployment = self.api_client_apps.read_namespaced_deployment(name=deployment_name, namespace=namespace)

        name = deployment.metadata.name
        namespace = deployment.metadata.namespace
        replicas = deployment.spec.replicas
        image = deployment.spec.template.spec.containers[0].image

        containers = deployment.spec.template.spec.containers
        resource_details = {}

        for container in containers:
            resources = container.resources
            resource_details[container.name] = {
                "requests": resources.requests if resources.requests is not None else None,
                "limits": resources.limits if resources.limits is not None else None,
            }

        return {
            "name": name,
            "namespace": namespace,
            "replicas": replicas,
            "image": image,
            "resources": resource_details,
        }

    def update_deployment(self, namespace, deployment_name, replicas=None, image=None):
        deployment = self.api_client_apps.read_namespaced_deployment(name=deployment_name, namespace=namespace)

        if image:
            deployment.spec.template.spec.containers[0].image = image

        if replicas:
            deployment.spec.replicas = replicas

        updated_deployment = self.api_client_apps.patch_namespaced_deployment(
            name=deployment_name, namespace=namespace, body=deployment
        )

        return {"data": updated_deployment.to_dict()}

    def get_deployment_logs(self, namespace, deployment, lines_to_tail):
        apps_v1_api = self.api_client_apps
        core_v1_api = self.api_client_core

        deployment = apps_v1_api.read_namespaced_deployment(
            name=deployment,
            namespace=namespace,
        )

        labels = deployment.spec.template.metadata.labels
        label_selector = ",".join([f"{key}={value}" for key, value in labels.items()])

        pods = core_v1_api.list_namespaced_pod(
            namespace=namespace,
            label_selector=label_selector,
        ).items

        logs = []
        for pod in pods:
            log_response = core_v1_api.read_namespaced_pod_log(
                name=pod.metadata.name,
                namespace=namespace,
                tail_lines=lines_to_tail,
            )
            logs.append({"pod_name": pod.metadata.name, "logs": log_response})

        return logs

    def rollback_deployment(self, namespace, deployment_name):
        apps_v1_api = self.api_client_apps
        rollback_options = client.V1RollbackConfig(
            kind="Deployment",
            name=deployment_name,
            rollback_to=client.V1RollbackConfigRollbackTo(revision=0),
        )
        api_response = apps_v1_api.create_namespaced_deployment_rollback(
            namespace=namespace,
            name=deployment_name,
            body=rollback_options,
        )
        return {"data": api_response.to_dict()}

    def get_deployment_status(self, namespace, deployment_name):
        api_client = self.api_client_apps
        api_response = api_client.read_namespaced_deployment_status(
            name=deployment_name,
            namespace=namespace,
        )
        return {
            "available_replicas": api_response.status.available_replicas,
            "updated_replicas": api_response.status.updated_replicas,
            "ready_replicas": api_response.status.ready_replicas,
        }

    def rollout_status(self, namespace, deployment_name):
        apps_api = self.api_client_apps
        deployment_status = apps_api.read_namespaced_deployment_status(
            name=deployment_name,
            namespace=namespace,
        )

        if deployment_status.spec.replicas != deployment_status.status.replicas:
            return {
                "status": "Rollout in progress",
                "details": {
                    "desired_replicas": deployment_status.spec.replicas,
                    "current_replicas": deployment_status.status.replicas,
                },
            }

        elif deployment_status.status.available_replicas != deployment_status.status.replicas:
            return {
                "status": "Rollout in progress",
                "details": {
                    "desired_available_replicas": deployment_status.spec.replicas,
                    "current_available_replicas": deployment_status.status.available_replicas,
                },
            }

        elif deployment_status.metadata.generation != deployment_status.status.observed_generation:
            return {
                "status": "Rollout in progress",
                "details": {
                    "observed_generation": deployment_status.status.observed_generation,
                    "current_generation": deployment_status.metadata.generation,
                },
            }

        return {
            "status": "Rollout complete",
            "details": {
                "desired_replicas": deployment_status.spec.replicas,
                "current_replicas": deployment_status.status.replicas,
                "desired_available_replicas": deployment_status.spec.replicas,
                "current_available_replicas": deployment_status.status.available_replicas,
                "observed_generation": deployment_status.status.observed_generation,
                "current_generation": deployment_status.metadata.generation,
            },
        }

    def rollout_restart_deployment(self, namespace, deployment_name):
        self.logger.info("restarting deployment " + deployment_name)
        api_client = self.api_client_apps

        def patch_deployment():
            nonlocal api_response
            api_response = api_client.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body={"spec": {"template": {"metadata": {"labels": {"date": str(time.time())}}}}},
            )

        api_response = None
        thread = threading.Thread(target=patch_deployment)
        thread.start()
        thread.join(timeout=10)
        self.logger.info("Restarted deployment " + deployment_name)

    def set_deployment_image(self, namespace, deployment_name, image):
        self.logger.info("setting image for deployment " + deployment_name)
        api_client = self.api_client_apps
        api_response = api_client.read_namespaced_deployment(deployment_name, namespace)
        api_response.spec.template.spec.containers[0].image = image
        api_response = api_client.patch_namespaced_deployment(deployment_name, namespace, api_response)
        return api_response.spec.template.spec.containers[0].image

    def get_deployment_image(self, namespace, deployment_name):
        self.logger.info("getting image for deployment " + deployment_name)
        api_client = KubernetesClient().get_apps_client()
        api_response = api_client.read_namespaced_deployment(deployment_name, namespace)
        return api_response.spec.template.spec.containers[0].image

    def get_deployment_replicas(self, namespace, deployment_name):
        self.logger.info("getting replicas for deployment " + deployment_name)
        api_client = self.api_client_core
        api_response = api_client.read_namespaced_deployment(deployment_name, namespace)
        self.logger.info("replicas for deployment " + deployment_name + " is " + str(api_response.spec.replicas))
        return api_response.spec.replicas

    def set_deployment_replicas(self, namespace, deployment_name, replicas):
        api_client = self.api_client_apps
        api_response = api_client.read_namespaced_deployment(deployment_name, namespace)
        api_response.spec.replicas = replicas
        api_response = api_client.patch_namespaced_deployment(deployment_name, namespace, api_response)
        return api_response.spec.replicas

    def list_deployment(self, namespace):
        self.logger.info("listing deployments")
        api_client = self.api_client_apps
        api_response = api_client.list_namespaced_deployment(namespace)
        self.logger.info("returning deployments")
        return [item.metadata.name for item in api_response.items]

    @retry(
        wait=wait_random_exponential(multiplier=0.5, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((DeploymentUpdateConflictError)),
    )
    def scale_deployment(self, namespace, deployment_name, replicas):
        try:
            self.logger.info(f"scaling deployment {deployment_name} to {replicas} replicas")
            api_client = self.api_client_apps
            deployment = api_client.read_namespaced_deployment(deployment_name, namespace)
            deployment.spec.replicas = replicas
            api_response = api_client.patch_namespaced_deployment(deployment_name, namespace, deployment)
            return {"status": "success", "replicas": api_response.spec.replicas}
        except ApiException as e:
            if e.status == 409:  # conflict error
                raise DeploymentUpdateConflictError(e.status, e.body) from None
            else:
                raise

    @retry(
        wait=wait_random_exponential(multiplier=0.5, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((DeploymentUpdateConflictError)),
    )
    def scale_deployment_resources_inner(self, namespace, deployment_name, container_name, requests, limits):
        try:
            self.logger.info(
                f"scaling deployment resources for deplyment: {deployment_name} container: {container_name} requests: {requests} limits: {limits}"
            )
            api_client = self.api_client_apps
            deployment = api_client.read_namespaced_deployment(deployment_name, namespace)

            for container in deployment.spec.template.spec.containers:
                if container.name == container_name:
                    container.resources.requests = requests
                    container.resources.limits = limits

            api_response = api_client.patch_namespaced_deployment(deployment_name, namespace, deployment)
            return {"status": "success", "replicas": api_response.spec.replicas}
        except ApiException as e:
            if e.status == 409:  # conflict error
                raise DeploymentUpdateConflictError(e.status, e.body) from None
            else:
                raise

    def scale_deployment_resources(
        self,
        namespace,
        deployment_name,
        container_name,
        requests_cpu,
        requests_memory,
        limits_cpu,
        limits_memory,
    ):
        requests = {"cpu": requests_cpu, "memory": requests_memory}
        limits = {"cpu": limits_cpu, "memory": limits_memory}
        return self.scale_deployment_resources_inner(namespace, deployment_name, container_name, requests, limits)

    def delete_deployment(self, namespace, deployment_name):
        self.logger.info(f"deleting deployment {deployment_name}")
        api_client = self.api_client_apps
        api_response = api_client.delete_namespaced_deployment(deployment_name, namespace)
        self.logger.info(api_response)

    def check_deployment_status(self, namespace, deployment_name):
        self.logger.info(f"checking deployment status for {deployment_name}")
        api_client = self.api_client_apps
        api_response = api_client.read_namespaced_deployment_status(deployment_name, namespace)
        self.logger.info(api_response)

    def create_deployment_object(self, image_name, image, replicas):
        container = client.V1Container(
            name=image_name,
            image=image,
            ports=[client.V1ContainerPort(container_port=80)],
        )

        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": image_name}),
            spec=client.V1PodSpec(containers=[container]),
        )

        spec = client.V1DeploymentSpec(
            replicas=replicas,
            template=template,
            selector={"matchLabels": {"app": image_name}},
        )

        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=f"{image_name}"),
            spec=spec,
        )

        return deployment

    def create_deployment(self, namespace, image_name, image, replicas=1):
        self.logger.info(f"creating deployment in namespace: {namespace} for image: {image}")
        deployment = self.create_deployment_object(image_name, image, replicas)
        api_client = self.api_client_apps
        api_response = api_client.create_namespaced_deployment(namespace, deployment)
        self.logger.info(api_response)
