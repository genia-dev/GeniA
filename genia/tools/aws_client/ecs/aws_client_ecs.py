import logging
import boto3

from genia.tools.aws_client.aws_client import AWSClient


class AWSClientECS(AWSClient):
    logger = logging.getLogger(__name__)

    def _restart_cluster(self, aws_access_key_id, aws_secret_access_key, region_name, cluster_name):
        resource = boto3.client(
            "ecs",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        response = resource.list_services(cluster=cluster_name)

        for service_arn in response["serviceArns"]:
            # force a new deployment for each service
            service_response = resource.update_service(
                cluster=cluster_name, service=service_arn, forceNewDeployment=True
            )
            self.logger.info("service %s is being restarted.", service_arn)
            self.logger.debug("update ecs service response: %s", service_response)

        return {"message": f"all ecs services in cluster {cluster_name} are being restarted."}

    def _list_clusters(self, aws_access_key_id, aws_secret_access_key, region_name):
        resource = boto3.client(
            "ecs",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        clusters = resource.list_clusters()
        return clusters["clusterArns"]

    def list_clusters(self, region_name):
        return self._list_clusters(self.aws_access_key_id, self.aws_secret_access_key, region_name)

    def restart_cluster(self, region_name, cluster_name):
        return self._restart_cluster(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            region_name,
            cluster_name,
        )
