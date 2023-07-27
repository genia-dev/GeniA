import concurrent.futures
import boto3
import json


class RepositoryInfoCollector:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        self.client = session.client("ecr")
        self.sts_client = session.client("sts")

    def _describe_repositories(self):
        paginator = self.client.get_paginator("describe_repositories")
        repository_names = [repo["repositoryName"] for page in paginator.paginate() for repo in page["repositories"]]
        return repository_names

    def _get_lifecycle_policy(self, repository_name):
        try:
            response = self.client.get_lifecycle_policy(repositoryName=repository_name)
            return json.loads(response["lifecyclePolicyText"])["rules"]
        except self.client.exceptions.LifecyclePolicyNotFoundException:
            return None

    def _describe_images(self, repository_name):
        paginator = self.client.get_paginator("describe_images")
        image_details = [
            image for page in paginator.paginate(repositoryName=repository_name) for image in page["imageDetails"]
        ]
        return len(image_details), sum([img["imageSizeInBytes"] for img in image_details])

    def _get_tags(self, repository_name):
        region_name = self.client.meta.region_name
        response = self.client.list_tags_for_resource(
            resourceArn=f"arn:aws:ecr:{region_name}:{self._get_account_id()}:repository/{repository_name}"
        )
        return response.get("tags", [])

    def _get_account_id(self):
        caller_identity = self.sts_client.get_caller_identity()
        return caller_identity["Account"]

    def _bytes_to_units(self, bytes):
        mb = bytes / (1024 * 1024)
        gb = mb / 1024
        tb = gb / 1024
        return mb, gb, tb

    def process_repository(self, repository_name):
        lifecycle_policy = self._get_lifecycle_policy(repository_name)
        image_count, total_size_bytes = self._describe_images(repository_name)
        total_size_mb, total_size_gb, total_size_tb = self._bytes_to_units(total_size_bytes)
        tags = self._get_tags(repository_name)

        return {
            "name": repository_name,
            "lifecycle_policy": lifecycle_policy,
            "image_count": image_count,
            "total_size_bytes": total_size_bytes,
            "total_size_mb": total_size_mb,
            "total_size_gb": total_size_gb,
            "total_size_tb": total_size_tb,
            "tags": tags,
        }

    def collect_repository_info(self):
        repository_names = self._describe_repositories()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return list(executor.map(self.process_repository, repository_names))

    def get_top_k_containers_usage(self, limit=10):
        repositories_info = self.collect_repository_info()
        sorted_repositories_info = sorted(repositories_info, key=lambda x: x["total_size_bytes"], reverse=True)
        usage = []
        for i, repo in enumerate(sorted_repositories_info[:limit]):
            usage.append(
                {
                    "name": repo["name"],
                    "image_count": repo["image_count"],
                    "lifecycle_policy": repo["lifecycle_policy"] if repo["lifecycle_policy"] is not None else "no",
                    "size": {
                        "bytes": f'{repo["total_size_bytes"]:.3f}',
                        "MB": f'{repo["total_size_mb"]:.3f}',
                        "GB": f'{repo["total_size_gb"]:.3f}',
                        "TB": f'{repo["total_size_tb"]:.3f}',
                    },
                }
            )
        return usage
