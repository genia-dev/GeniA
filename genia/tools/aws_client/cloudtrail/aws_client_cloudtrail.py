import json
import logging
from datetime import datetime, timedelta
import boto3

from genia.tools.aws_client.aws_client import AWSClient


class AWSClientCloudTrail(AWSClient):
    logger = logging.getLogger(__name__)

    def _list_users_in_group_more_than_x_time(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        user_group,
        age_seconds,
        lookup_window_days=7,
    ):
        session = boto3.Session(
            # CloudTrail events in `us-east-1` specifically
            region_name="us-east-1",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        client = session.client("cloudtrail")

        start_time = datetime.utcnow() - timedelta(days=lookup_window_days)

        add_response = client.lookup_events(
            LookupAttributes=[{"AttributeKey": "EventName", "AttributeValue": "AddUserToGroup"}],
            StartTime=start_time,
        )

        remove_response = client.lookup_events(
            LookupAttributes=[{"AttributeKey": "EventName", "AttributeValue": "RemoveUserFromGroup"}],
            StartTime=start_time,
        )

        add_events = add_response.get("Events", [])
        remove_events = remove_response.get("Events", [])

        added_users = {}
        for event in add_events:
            event_dict = json.loads(event["CloudTrailEvent"])
            groupname = event_dict["requestParameters"]["groupName"]

            if groupname == user_group:
                username = event_dict["requestParameters"]["userName"]
                add_time = event["EventTime"]
                added_users[(username, groupname)] = add_time

        removed_users = {}
        for event in remove_events:
            event_dict = json.loads(event["CloudTrailEvent"])
            groupname = event_dict["requestParameters"]["groupName"]
            if groupname == user_group:
                username = event_dict["requestParameters"]["userName"]
                remove_time = event["EventTime"]
                removed_users[(username, groupname)] = remove_time

        users = []
        for (username, groupname), add_time in added_users.items():
            if (username, groupname) not in removed_users or removed_users[
                (username, groupname)
            ] > add_time + timedelta(seconds=age_seconds):
                users.append(username)
        return users

    def list_users_in_group_more_than_x_time(self, user_group, age_seconds):
        return self._list_users_in_group_more_than_x_time(
            self.aws_access_key_id, self.aws_secret_access_key, user_group, age_seconds
        )
