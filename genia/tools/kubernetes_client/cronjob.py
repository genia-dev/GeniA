import logging

from genia.tools.kubernetes_client.kubernetes_clients import KubernetesClient
from kubernetes import client


class KubernetesCronJob:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.api_client = KubernetesClient().get_batch_client()

    def list_suspended_cronjobs(self):
        api_client = self.api_client
        api_response = api_client.list_cron_job_for_all_namespaces()
        suspended_cronjobs = [cj for cj in api_response.items if cj.spec.suspend == True]
        return [item.metadata.name for item in suspended_cronjobs]

    def list_suspended_cronjobs_for_namespace(self, namespace):
        api_client = self.api_client
        api_response = api_client.list_namespaced_cron_job(namespace)
        suspended_cronjobs = [cj for cj in api_response.items if cj.spec.suspend == True]
        return [item.metadata.name for item in suspended_cronjobs]

    def list_disabled_cronjobs_for_all_namespaces(self):
        api_client = self.api_client
        api_response = api_client.list_cron_job_for_all_namespaces()
        return [item.metadata.name for item in api_response.items if item.spec.schedule == ""]

    def list_disabled_cronjobs_for_namespace(self, namespace):
        api_client = self.api_client
        api_response = api_client.list_namespaced_cron_job(namespace)
        return [item.metadata.name for item in api_response.items if item.spec.schedule == ""]

    def list_enabled_cronjobs_for_namespace(self, namespace):
        api_client = self.api_client
        api_response = api_client.list_namespaced_cron_job(namespace)
        return [item.metadata.name for item in api_response.items if item.spec.schedule != ""]

    def delete_stuck_cronjob(self):
        api_client = self.api_client
        api_response = api_client.list_cron_job_for_all_namespaces()
        stuck_cronjobs = [cj for cj in api_response.items if cj.spec.suspend == True]
        for cronjob in stuck_cronjobs:
            api_client.delete_namespaced_cron_job(cronjob.metadata.name, cronjob.metadata.namespace)

        return [item.metadata.name for item in stuck_cronjobs]

    def suspend_cronjob(self, namespace, cron_job_name):
        api_client = self.api_client
        api_response = api_client.patch_namespaced_cron_job(cron_job_name, namespace, {"spec": {"suspend": True}})
        self.logger.info(api_response)

    def unsuspend_cronjob(self, namespace, cron_job_name):
        api_client = self.api_client
        api_response = api_client.patch_namespaced_cron_job(cron_job_name, namespace, {"spec": {"suspend": False}})
        self.logger.info(api_response)

    def create_cronjob_object(self, name, schedule, command, image):
        job_template = client.V1PodTemplateSpec()
        job_template.spec = client.V1PodSpec(
            containers=[client.V1Container(name=name, image=image, args=command)],
            restart_policy="OnFailure",
        )

        cronjob_spec = client.V1CronJobSpec(
            job_template=client.V1JobTemplateSpec(spec=client.V1JobSpec(template=job_template)),
            schedule=schedule,
        )

        cronjob = client.V1CronJob(
            api_version="batch/v1",
            kind="CronJob",
            metadata=client.V1ObjectMeta(name=name),
            spec=cronjob_spec,
        )

        return cronjob

    def create_cronjob(self, name, namespace, schedule, command, image):
        cronjob = self.create_cronjob_object(name=name, schedule=schedule, command=command, image=image)

        api_response = self.api_client.create_namespaced_cron_job(namespace=namespace, body=cronjob)
        self.logger.info(api_response)
