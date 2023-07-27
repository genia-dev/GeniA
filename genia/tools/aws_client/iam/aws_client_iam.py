import logging
import boto3
import json

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

    def _list_roles(
        self,
        aws_access_key_id,
        aws_secret_access_key,
    ):
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        iam = session.client("iam")
        response = iam.list_roles()

        self.logger.debug(f"list roles response: {response}")

        roles = []
        for role in response["Roles"]:
            roles.append(role["RoleName"])
        return roles

    def _attach_policy_to_role(self, aws_access_key_id, aws_secret_access_key, role_name, policy):
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        iam = session.client("iam")
        policy_name = role_name + policy.replace(":", "")

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": policy, "Resource": "*"}],
        }

        policy_json = json.dumps(policy_document)
        response = iam.put_role_policy(RoleName=role_name, PolicyName=policy_name, PolicyDocument=policy_json)

        self.logger.debug(f"attach policy to role response: {response}")

    def list_users_in_group(self, group_name):
        return self._list_users_in_group(self.aws_access_key_id, self.aws_secret_access_key, group_name)

    def add_user_to_group(self, user_name, group_name):
        return self._add_user_to_group(self.aws_access_key_id, self.aws_secret_access_key, user_name, group_name)

    def remove_user_from_group(self, user_name, group_name):
        return self._remove_user_from_group(self.aws_access_key_id, self.aws_secret_access_key, user_name, group_name)

    def list_roles(self):
        return self._list_roles(self.aws_access_key_id, self.aws_secret_access_key)

    def attach_policy_to_role(self, role_name, policy):
        return self._attach_policy_to_role(self.aws_access_key_id, self.aws_secret_access_key, role_name, policy)
