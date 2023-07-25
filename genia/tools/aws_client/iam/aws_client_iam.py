import logging
import boto3

from genia.tools.aws_client.aws_client import AWSClient


class AWSClientIAM(AWSClient):
    logger = logging.getLogger(__name__)

    def _list_users_in_group(self, aws_access_key_id, aws_secret_access_key, group_name):
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        client = session.client("iam")
        response = client.get_group(GroupName=group_name)
        users = response.get("Users", [])

        result = []
        for user in users:
            username = user.get("UserName")
            result.append(username)
        return result

    def _add_user_to_group(self, aws_access_key_id, aws_secret_access_key, user_name, group_name):
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        client = session.client("iam")

        response = client.add_user_to_group(GroupName=group_name, UserName=user_name)

        self.logger.debug(f"add user to group response: {response}")

    def _remove_user_from_group(self, aws_access_key_id, aws_secret_access_key, user_name, group_name):
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        client = session.client("iam")

        response = client.remove_user_from_group(GroupName=group_name, UserName=user_name)

        self.logger.debug(f"remove user from group response: {response}")

    def list_users_in_group(self, group_name):
        return self._list_users_in_group(self.aws_access_key_id, self.aws_secret_access_key, group_name)

    def add_user_to_group(self, user_name, group_name):
        return self._add_user_to_group(self.aws_access_key_id, self.aws_secret_access_key, user_name, group_name)

    def remove_user_from_group(self, user_name, group_name):
        return self._remove_user_from_group(self.aws_access_key_id, self.aws_secret_access_key, user_name, group_name)
