import json
import boto3
import logging

from genia.tools.aws_client.aws_client import AWSClient


class AWSClientEC2(AWSClient):
    logger = logging.getLogger(__name__)

    def _get_running_instances(self, aws_access_key_id, aws_secret_access_key, region_name):
        ec2_resource = boto3.resource(
            "ec2",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        instances = ec2_resource.instances.filter(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])

        result = []
        for instance in instances:
            result.append(instance.id)

        return json.dumps(result)

    def _terminate_instance(self, aws_access_key_id, aws_secret_access_key, region_name, instance_id):
        ec2_resource = boto3.resource(
            "ec2",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        instance = ec2_resource.Instance(instance_id)
        response = instance.terminate()
        return response

    def _list_aws_regions(self, aws_access_key_id, aws_secret_access_key):
        ec2_resource = boto3.client(
            "ec2",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        regions = ec2_resource.describe_regions()["Regions"]
        regions = [region["RegionName"] for region in regions]
        self.logger.debug("regions= %s", str(regions))
        return regions

    def get_running_instances(self, region_name):
        return self._get_running_instances(self.aws_access_key_id, self.aws_secret_access_key, region_name)

    def terminate_instance(self, region_name, instance_id):
        return self._terminate_instance(self.aws_access_key_id, self.aws_secret_access_key, region_name, instance_id)

    def list_aws_regions(self):
        return self._list_aws_regions(self.aws_access_key_id, self.aws_secret_access_key)
