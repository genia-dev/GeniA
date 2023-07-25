import os
import logging
import requests
from jinja2 import Template


class ArgoClient:
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        argo_url=None,
        argo_token=None,
        argo_workflows_url=None,
        argo_workflows_token=None,
    ):
        if argo_token is None:
            self.argo_token = os.getenv("ARGO_TOKEN")

        if argo_workflows_token is None:
            self.argo_workflows_token = os.getenv("ARGO_WORKFLOWS_TOKEN")

        if argo_url is None:
            self.argo_url = os.getenv("ARGO_URL")

        if argo_workflows_url is None:
            self.argo_workflows_url = os.getenv("ARGO_WORKFLOWS_URL")

        self.tls_verify = os.getenv("PYTHON_ENV") != "development"

    def get_base_headers(self, token):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        return headers

    def get_version(self):
        r = requests.get(
            f"{self.argo_url}/api/version",
            headers=self.get_base_headers(self.argo_token),
            verify=self.tls_verify,
        )
        self.logger.debug(f"argo response for get_version: {r}")
        r.raise_for_status()

        return r.json()

    def get_applications(self):
        r = requests.get(
            f"{self.argo_url}/api/v1/applications",
            headers=self.get_base_headers(self.argo_token),
            verify=self.tls_verify,
        )
        self.logger.debug(f"argo response for get_applications: {r}")
        r.raise_for_status()

        data = r.json()
        applications = {}

        if data["items"] is not None:
            for app in data["items"]:
                app_name = app["metadata"]["name"]
                health_status = app["status"]["health"]["status"]
                applications[f"Application Name: {app_name}"] = f"Health Status: {health_status}"

        return applications

    def get_applications_logs_by_app(self, app, sinceSeconds=3600, tailLines=42):
        r = requests.get(
            f"{self.argo_url}/api/v1/applications/{app}/logs?sinceSeconds={sinceSeconds}&tailLines={tailLines}",
            headers=self.get_base_headers(self.argo_token),
            verify=self.tls_verify,
        )
        r.raise_for_status()
        self.logger.debug(f"argo response for get_applications_logs_by_app: {r}")

        return r.text

    def get_clusters(self):
        r = requests.get(
            f"{self.argo_url}/api/v1/clusters",
            headers=self.get_base_headers(self.argo_token),
            verify=self.tls_verify,
        )
        r.raise_for_status()
        self.logger.debug(f"argo response for get_clusters {r}")

        clusters = {}

        for server in r.json()["items"]:
            server_name = server["server"]
            connection_state = server["connectionState"]
            clusters[f"Server Name: {server_name}"] = f"Info: {connection_state}"

        return clusters

    def get_workflow_log(self, namespace, workflow_name, sinceSeconds=3600, tailLines=42):
        # logOptions.container=init
        # logOptions.container=wait

        r = requests.get(
            f"{self.argo_workflows_url}/api/v1/workflows/{namespace}/{workflow_name}/log?logOptions.container=main&logOptions.sinceSeconds={sinceSeconds}&logOptions.tailLines={tailLines}",
            headers=self.get_base_headers(self.argo_workflows_token),
            verify=self.tls_verify,
        )
        r.raise_for_status()
        self.logger.debug(f"argo response for get_applications_logs_by_app: {r}")

        return r.text

    def get_workflow(self, namespace, workflow_name):
        r = requests.get(
            f"{self.argo_workflows_url}/api/v1/workflows/{namespace}/{workflow_name}",
            headers=self.get_base_headers(self.argo_workflows_token),
            verify=self.tls_verify,
        )
        r.raise_for_status()
        self.logger.debug(f"argo response for get workflow {r}")
        data = r.json()

        name = data["metadata"]["name"]
        namespace = data["metadata"]["namespace"]
        creation_timestamp = data["metadata"]["creationTimestamp"]
        status_phase = data["status"]["phase"]
        container_image = data["spec"]["templates"][0]["container"]["image"]

        return {
            "name": name,
            "namespace": namespace,
            "creation_timestamp": creation_timestamp,
            "status_phase": status_phase,
            "container_image": container_image,
        }

    def submit_workflow_inner(self, workflow_name, namespace, image):
        with open("genia/tools/argo/workflow_template.json", "r") as file:
            template = Template(file.read())

        workflow = template.render(workflow_name=workflow_name, namespace=namespace, image=image)
        self.logger.debug(f"argo workflow before submmiting: {workflow}")
        r = requests.post(
            f"{self.argo_workflows_url}/api/v1/workflows/{namespace}",
            headers=self.get_base_headers(self.argo_workflows_token),
            verify=self.tls_verify,
            data=workflow,
        )
        r.raise_for_status()
        self.logger.debug(f"argo response for submit workflow {r}")
        data = r.json()
        return data["metadata"]["name"]

    def submit_workflow(self, workflow_name, namespace, image):
        generated_workflow = self.submit_workflow_inner(workflow_name, namespace, image)
        return f"succeed to submit workflow, the name of the created workflow is: {generated_workflow}"
