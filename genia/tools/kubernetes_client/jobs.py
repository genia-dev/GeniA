import datetime
import logging
import time
from datetime import timedelta

from kubernetes.client import (
    V1Container,
    V1EnvVar,
    V1Job,
    V1JobSpec,
    V1ObjectMeta,
    V1PodSpec,
    V1PodTemplateSpec,
)

from genia.tools.kubernetes_client.kubernetes_clients import KubernetesClient


class KubernetesJobs:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.api_client_core = KubernetesClient().get_core_api_client()
        self.api_client_batch = KubernetesClient().get_batch_client()
        self.default_timeout = 10

    def get_job_status(self, namespace, job_name):
        api_response = self.api_client_batch.read_namespaced_job(job_name, namespace)
        status = api_response.status
        return {
            "active": status.active,
            "succeeded": status.succeeded,
            "failed": status.failed,
            "parallelism": api_response.spec.parallelism,
            "completions": api_response.spec.completions,
        }

    def get_job_events(self, namespace, job_name):
        api_response = self.api_client_core.list_namespaced_event(
            namespace,
            field_selector=f"involvedObject.kind=Job,involvedObject.name={job_name}",
        )
        return [event.message for event in api_response.items]

    def suspend_job(self, namespace, job_name):
        api_response = self.api_client_batch.read_namespaced_job(job_name, namespace)
        api_response.spec.suspend = True
        api_response = self.api_client_batch.patch_namespaced_job(job_name, namespace, api_response)
        self.logger.info(api_response)

    def resume_job(self, namespace, job_name):
        api_response = self.api_client_batch.read_namespaced_job(job_name, namespace)
        api_response.spec.suspend = False
        api_response = self.api_client_batch.patch_namespaced_job(job_name, namespace, api_response)
        self.logger.info(api_response)

    def wait_for_job_completion(self, namespace, job_name, timeout):
        start_time = time.time()
        while time.time() - start_time < timeout:
            api_response = self.api_client_batch.read_namespaced_job(job_name, namespace)
            if api_response.status.succeeded is not None:
                return {"status": "completed"}
            time.sleep(5)
        return {"status": "timeout"}

    def create_namespaced_job(
        self,
        namespace,
        job_name,
        container_name,
        image,
        app_label,
        timeout_secs=3,
        parallelism=1,
        completions=1,
        restart_policy="Never",
        env_vars=None,
    ):
        start_time = datetime.datetime.now()
        timeout_time = start_time + timedelta(seconds=timeout_secs)

        self.logger.info("attempting to create namespaced job")

        if not env_vars:
            env_vars = {"EXAMPLE_ENV_VAR": "example-value"}
        container = V1Container(
            name=container_name,
            image=image,
            env=[V1EnvVar(name=k, value=v) for k, v in env_vars.items()],
        )

        job_spec = V1JobSpec(
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels={"app": app_label}),
                spec=V1PodSpec(
                    containers=[container],
                    restart_policy=restart_policy,
                ),
            ),
            backoff_limit=4,
            parallelism=parallelism,
            completions=completions,
        )

        new_job = V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=V1ObjectMeta(name=job_name),
            spec=job_spec,
        )

        api_response = self.api_client_batch.create_namespaced_job(namespace=namespace, body=new_job)
        self.logger.info(f"job created. response='{str(api_response)}")

        while datetime.datetime.now() < timeout_time:
            self.logger.info("Waiting for job to start")
            api_response = self.api_client_batch.read_namespaced_job(job_name, namespace)
            self.logger.info(f"current status: {api_response}")

            if api_response.status.active not in [None, 0]:
                return {"status": api_response.status.active}
            # TODO
            time.sleep(1.5)

    def delete_namespaced_job(self, namespace, job_name):
        api_response = self.api_client_batch.delete_namespaced_job(
            job_name, namespace, propagation_policy="Background"
        )
        self.logger.info(f"job deleted. response='{str(api_response)}")

    def list_namespaced_jobs(self, namespace):
        jobs = []

        api_response = self.api_client_batch.list_namespaced_job(namespace)
        self.logger.info(f"job listed. response='{str(api_response)}")
        for item in api_response.items:
            jobs.append(item.metadata.name)
        return jobs

    def get_namespaced_job_logs(self, namespace, job_name):
        while True:
            label_selector = f"job-name={job_name}"
            pod_list = self.api_client_core.list_namespaced_pod(namespace, label_selector=label_selector)
            if len(pod_list.items) > 0:
                break
            time.sleep(1)
        pod_name = pod_list.items[0].metadata.name
        self.logger.info(f"found pod:{pod_name}")

        while True:
            pod = self.api_client_core.read_namespaced_pod(pod_name, namespace)
            if pod.status.phase != "Pending":
                logs = self.api_client_core.read_namespaced_pod_log(pod_name, namespace)
                return logs.splitlines()
            time.sleep(1)

    def get_job_controller_uid(self, namespace, job_name):
        api_response = self.api_client_batch.read_namespaced_job(job_name, namespace)
        return api_response.metadata.labels["controller-uid"]
