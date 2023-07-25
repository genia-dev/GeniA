import json
import boto3
import logging

from genia.tools.aws_client.aws_client import AWSClient


class AWSClientSQS(AWSClient):
    logger = logging.getLogger(__name__)

    def _get_available_subresources(self, aws_access_key_id, aws_secret_access_key, region_name, queue_name):
        resource = boto3.resource(
            "sqs",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        queue = resource.get_queue_by_name(QueueName=queue_name)
        return {"data": queue.attributes}

    def _receive_sqs_messages(self, aws_access_key_id, aws_secret_access_key, region_name, queue_name):
        resource = boto3.resource(
            "sqs",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        queue = resource.get_queue_by_name(QueueName=queue_name)
        messages = queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=4)
        json_messages = []
        for message in messages:
            message_dict = message.attributes or {}
            message_dict["message_id"] = message.message_id
            message_dict["body"] = message.body
            json_messages.append(json.dumps(message_dict))
        return json_messages

    def _return_sqs_messages_to_queue(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        region_name,
        queue_name,
        message_id,
    ):
        resource = boto3.resource(
            "sqs",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        queue = resource.get_queue_by_name(QueueName=queue_name)
        queue_url = resource.get_queue_url(QueueName=queue_name)["QueueUrl"]
        response = resource.receive_message(
            QueueUrl=queue_url,
            AttributeNames=["All"],
            MaxNumberOfMessages=1,
            MessageAttributeNames=["All"],
            WaitTimeSeconds=0,
        )
        if "Messages" in response:
            message = response["Messages"][0]
            if message["MessageId"] == message_id:
                receipt_handle = message["ReceiptHandle"]
                resource.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
                return "OK"
            else:
                return "Message ID not found"
        else:
            return "No messages in the queue"

    def _list_sqs_queues(self, aws_access_key_id, aws_secret_access_key, region_name):
        resource = boto3.resource(
            "sqs",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        queues = resource.queues.all()
        return [queue.url for queue in queues]

    def get_available_subresources(self, region_name, queue_name):
        return self._get_available_subresources(
            self.aws_access_key_id, self.aws_secret_access_key, region_name, queue_name
        )

    def receive_sqs_messages(self, region_name, queue_name):
        return self._receive_sqs_messages(self.aws_access_key_id, self.aws_secret_access_key, region_name, queue_name)

    def return_sqs_messages_to_queue(self, region_name, queue_name, message_id):
        return self._return_sqs_messages_to_queue(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            region_name,
            queue_name,
            message_id,
        )

    def list_sqs_queues(self, region_name):
        return self._list_sqs_queues(self.aws_access_key_id, self.aws_secret_access_key, region_name)
