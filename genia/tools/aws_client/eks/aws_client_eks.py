import logging
import boto3

from genia.tools.aws_client.aws_client import AWSClient


class AWSClientEKS(AWSClient):
    # Set up a logger for this class
    logger = logging.getLogger(__name__)

    def _list_clusters_eks(self, aws_access_key_id, aws_secret_access_key, region_name):
        try:
            self.logger.info("Creating EKS client for region: %s", region_name)
            client = boto3.client(
                "eks",
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )

            self.logger.debug("Listing EKS clusters")
            clusters = client.list_clusters()

            self.logger.info("EKS clusters retrieved successfully")
            return clusters["clusters"]
        except Exception as e:
            self.logger.error("Error in listing EKS clusters: %s", e)
            raise

    def list_clusters_eks(self, region_name):
        self.logger.info("Listing EKS clusters for region: %s", region_name)
        return self._list_clusters_eks(self.aws_access_key_id, self.aws_secret_access_key, region_name)

    def describe_cluster_eks(self, cluster_name, region_name):
        try:
            self.logger.info("Creating EKS client for region: %s", region_name)
            client = boto3.client(
                "eks",
                region_name=region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )

            self.logger.debug("Describing EKS cluster: %s", cluster_name)
            cluster_description = client.describe_cluster(name=cluster_name)

            self.logger.info("EKS cluster description retrieved successfully")
            return cluster_description["cluster"]
        except Exception as e:
            self.logger.error("Error in describing EKS cluster '%s': %s", cluster_name, e)
            raise
