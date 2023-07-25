import os
from typing import Any


class AWSClient:
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region_name=None):
        if aws_access_key_id is None:
            self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        if aws_secret_access_key is None:
            self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        if region_name is None:
            self.region_name = os.getenv("AWS_DEFAULT_REGION")

    def exec(self) -> Any:
        pass
