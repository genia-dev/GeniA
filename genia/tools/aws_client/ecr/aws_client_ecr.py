import logging

from genia.tools.aws_client.aws_client import AWSClient
from genia.tools.aws_client.ecr.repository_info_collector import RepositoryInfoCollector


class AWSClientECR(AWSClient):
    logger = logging.getLogger(__name__)

    def get_top_k_containers_usage(self, region_name, limit=10):
        usage = RepositoryInfoCollector(self.aws_access_key_id, self.aws_secret_access_key, region_name)
        return usage.get_top_k_containers_usage(limit)
