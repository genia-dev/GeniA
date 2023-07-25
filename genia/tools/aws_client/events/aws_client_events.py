import logging
import uuid

import boto3

from genia.tools.aws_client.aws_client import AWSClient


class AWSClientEvents(AWSClient):
    logger = logging.getLogger(__name__)

    def _create_scheduled_lambda(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        region_name,
        cron_expression,
        lambda_function_name,
    ):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        client = session.client("events")

        response = client.put_rule(
            Name=f"scheduledLambda{lambda_function_name}",
            ScheduleExpression=f"cron({cron_expression})",
            State="ENABLED",
        )

        rule_arn = response["RuleArn"]

        lambda_client = session.client("lambda")
        response = lambda_client.get_function(FunctionName=lambda_function_name)
        lambda_function_arn = response["Configuration"]["FunctionArn"]

        self.logger.info(f"the function {lambda_function_name} arn is: {lambda_function_arn}")

        lambda_client.add_permission(
            FunctionName=lambda_function_arn,
            StatementId=str(uuid.uuid4()),
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com",
            SourceArn=rule_arn,
        )

        response = client.put_targets(
            Rule=f"scheduledLambda{lambda_function_name}",
            Targets=[
                {
                    "Arn": lambda_function_arn,
                    "Id": f"myCloudWatchEventsTarget{lambda_function_name}",
                },
            ],
        )

        self.logger.info("successfully create scheduled lambda: {}".format(response))
        return f"successfully create scheduled lambda: {lambda_function_name}"

    def _list_scheduled_lambdas(self, aws_access_key_id, aws_secret_access_key, region_name):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        client = session.client("events")
        response = client.list_rules()

        return response["Rules"]

    def _update_scheduled_lambda(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        region_name,
        lambda_function_name,
        cron_expression,
    ):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        client = session.client("events")

        response = client.put_rule(
            Name=f"scheduledLambda{lambda_function_name}",
            ScheduleExpression=cron_expression,
            State="ENABLED",
        )

        self.logger.info("successfully updated lambda schedule: {}".format(response))
        return f"successfully update scheduled lambda: {lambda_function_name}"

    def _delete_scheduled_lambda(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        region_name,
        lambda_function_name,
    ):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        client = session.client("events")

        client.remove_targets(
            Rule=f"scheduledLambda{lambda_function_name}",
            Ids=[f"myCloudWatchEventsTarget{lambda_function_name}"],
        )

        response = client.delete_rule(Name=f"scheduledLambda{lambda_function_name}")

        self.logger.info("successfully deleted Lambda schedule: {}".format(response))
        return f"successfully deleted scheduled lambda: {lambda_function_name}"

    def create_scheduled_lambda(self, region_name, cron_expression, lambda_function_name):
        return self._create_scheduled_lambda(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            region_name,
            cron_expression,
            lambda_function_name,
        )

    def list_scheduled_lambdas(self, region_name):
        return self._list_scheduled_lambdas(self.aws_access_key_id, self.aws_secret_access_key, region_name)

    def update_scheduled_lambda(self, region_name, lambda_function_name, cron_expression):
        return self._update_scheduled_lambda(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            region_name,
            cron_expression,
            lambda_function_name,
        )

    def delete_scheduled_lambda(self, region_name, lambda_function_name):
        return self._delete_scheduled_lambda(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            region_name,
            lambda_function_name,
        )
