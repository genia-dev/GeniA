import io
import json
import logging
import os
import shutil
import tarfile
import tempfile
import time
import zipfile
from io import BytesIO

import boto3
import docker
import requests

from genia.tools.aws_client.aws_client import AWSClient
from genia.utils.utils import generate_random_string


class AWSClientLambda(AWSClient):
    logger = logging.getLogger(__name__)

    def _get_lambda_function_code(self, aws_access_key_id, aws_secret_access_key, region_name, function_name):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        client = session.client("lambda")

        try:
            response = client.get_function(FunctionName=function_name)
            presigned_url = response["Code"]["Location"]
            r = requests.get(presigned_url)

            temp_zip = tempfile.NamedTemporaryFile(delete=False)
            temp_zip.write(r.content)
            temp_zip.close()

            full_content = ""
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(temp_zip.name, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)

                # TODO
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file == "main.py":
                            file_path = os.path.join(root, file)
                            with open(file_path, "r") as f:
                                full_content += f.read()
        finally:
            if temp_zip:
                os.remove(temp_zip.name)

        return full_content

    def _update_lambda(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        region_name,
        function_name,
        lambda_code,
    ):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        client = session.client("lambda")
        zipped = self._create_lambda_zip(lambda_code)
        response = client.update_function_code(FunctionName=function_name, ZipFile=zipped)

        self.logger.info("update lambda response: %s", response)
        return "succeed to update lambda function " + function_name

    def _invoke_lambda(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        region_name,
        function_name,
        payload,
    ):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        lambda_client = session.client("lambda")

        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=payload,
        )

        self.logger.info("invoke lambda %s response: %s", function_name, response)
        return {"message": json.load(response["Payload"])}

    def _create_lambda_zip(
        self,
        content,
        base_dir="/app",
        docker_image="geniadev/aws-lambda-python-builder",
        zip_name="lambda.zip",
    ):
        temp_dir = None
        container = None
        try:
            temp_dir = tempfile.mkdtemp()
            self.logger.debug((f"temporary directory path is {temp_dir}"))
            local_file_path = os.path.join(temp_dir, "main.py")

            with open(local_file_path, "w") as file:
                file.write(content)

            client = docker.from_env()

            container_name = f"aws-lambda-python-builder-{generate_random_string()}"
            self.logger.debug(f"create lambda zip container name: {container_name}")
            container = client.containers.run(docker_image, command=[], detach=True, name=container_name)

            tarstream = BytesIO()
            with tarfile.open(fileobj=tarstream, mode="w") as tar:
                tar.add(local_file_path, arcname=os.path.basename(local_file_path))
            tarstream.seek(0)

            container.put_archive(base_dir, tarstream)

            exit_code, output = container.exec_run(f"bash -c 'cd {base_dir} && zip -u {zip_name} main.py'")

            if exit_code != 0:
                raise Exception(f"failed to add file to zip archive: {output}")

            data, stat = container.get_archive(f"{base_dir}/{zip_name}")
            self.logger.debug(f"get archive from docker stat: {stat}")

            tar_data = io.BytesIO(b"".join(data))
            with tarfile.open(fileobj=tar_data) as tar:
                tar.extractall(path=temp_dir)

            with open(f"{temp_dir}/{zip_name}", "rb") as f:
                zip_content = f.read()
            return zip_content
        finally:
            if container:
                container.stop()
                container.remove()
            if temp_dir:
                self.logger.debug(f"going to delete temp dir: {temp_dir}")
                shutil.rmtree(temp_dir)

    def _delete_iam_role(self, aws_access_key_id, aws_secret_access_key, region_name, role_name):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        iam_client = session.client("iam")
        policies = iam_client.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]
        for policy in policies:
            iam_client.detach_role_policy(RoleName=role_name, PolicyArn=policy["PolicyArn"])

        inline_policies = iam_client.list_role_policies(RoleName=role_name)["PolicyNames"]
        for policy_name in inline_policies:
            iam_client.delete_role_policy(RoleName=role_name, PolicyName=policy_name)

        iam_client.delete_role(RoleName=role_name)
        self.logger.info(f"successfully deleted IAM role: {role_name}")

    def _delete_api_gateway_resources(self, aws_access_key_id, aws_secret_access_key, region_name, function_arn):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        apigw_client = session.client("apigateway")
        apis = apigw_client.get_rest_apis()["items"]
        for api in apis:
            resources = apigw_client.get_resources(restApiId=api["id"])["items"]
            for resource in resources:
                try:
                    methods = resource["resourceMethods"]
                except KeyError:
                    continue

                for method in methods:
                    try:
                        integration = apigw_client.get_integration(
                            restApiId=api["id"],
                            resourceId=resource["id"],
                            httpMethod=method,
                        )
                    except apigw_client.exceptions.NotFoundException:
                        continue

                    if function_arn in integration["uri"]:
                        apigw_client.delete_integration(
                            restApiId=api["id"],
                            resourceId=resource["id"],
                            httpMethod=method,
                        )
            apigw_client.delete_rest_api(restApiId=api["id"])

    def _delete_lambda(self, aws_access_key_id, aws_secret_access_key, region_name, function_name):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        lambda_client = session.client("lambda")
        role_name = None

        response = lambda_client.get_function(FunctionName=function_name)
        role_arn = response["Configuration"]["Role"]
        role_name = role_arn.split("/")[-1]
        function_arn = response["Configuration"]["FunctionArn"]
        self.logger.info(f"successfully get function: {function_name}")

        response = lambda_client.delete_function(FunctionName=function_name)
        self.logger.info(f"successfully deleted lambda function: {function_name}")

        self._delete_iam_role(aws_access_key_id, aws_secret_access_key, region_name, role_name)
        self._delete_api_gateway_resources(aws_access_key_id, aws_secret_access_key, region_name, function_arn)

    def _create_lambda(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        region_name,
        function_name,
        lambda_code,
        function_handler,
    ):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        iam = session.client("iam")

        assume_role_policy_document = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "",
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }
        )

        fixed_function_name = (
            function_name  #''.join(char for char in function_name if char.isalpha() and ord(char) < 128)
        )
        create_role_response = iam.create_role(
            RoleName=f"lambda-execute-role-{fixed_function_name}",
            AssumeRolePolicyDocument=assume_role_policy_document,
        )

        self.logger.debug(f"create role response: {create_role_response}")

        role_arn = create_role_response["Role"]["Arn"]

        inline_policy = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Action": ["apigateway:*"], "Resource": ["*"]}],
            }
        )

        iam.put_role_policy(
            RoleName=f"lambda-execute-role-{fixed_function_name}",
            PolicyName="APIGatewayManagement",
            PolicyDocument=inline_policy,
        )

        iam.attach_role_policy(
            RoleName=f"lambda-execute-role-{fixed_function_name}",
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSlambdaBasicExecutionRole",
        )

        # TODO
        time.sleep(10)

        lambda_client = session.client("lambda")
        response = lambda_client.create_function(
            FunctionName=fixed_function_name,
            Runtime="python3.8",
            Role=role_arn,
            Handler=f"main.{function_handler}",
            Code={"ZipFile": self._create_lambda_zip(lambda_code)},
            Description=f"lambda function for {fixed_function_name}",
            Timeout=10,
            MemorySize=128,
        )

        self.logger.debug(f"create lambda function response: {response}")

        api_client = session.client("apigateway")
        api_response = api_client.create_rest_api(
            name=f"{fixed_function_name}API",
            description=f"API Gateway for {fixed_function_name}",
            endpointConfiguration={
                "types": [
                    "REGIONAL",
                ]
            },
        )
        self.logger.debug(f"create api gateway rest api function response: {api_response}")

        lambda_arn = response["FunctionArn"]
        account_id = role_arn.split(":")[4]

        api_id = api_response["id"]
        parent_id = api_client.get_resources(restApiId=api_id)["items"][0]["id"]
        resource_response = api_client.create_resource(
            restApiId=api_id, parentId=parent_id, pathPart=fixed_function_name
        )
        self.logger.debug(f"create api gateway resource response: {resource_response}")

        resource_id = resource_response["id"]
        method_response = api_client.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod="POST",
            authorizationType="NONE",
        )

        self.logger.debug(f"api gateway put method response: {method_response}")

        integration_response = api_client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod="POST",
            type="AWS_PROXY",
            integrationHttpMethod="POST",
            uri="arn:aws:apigateway:{}:lambda:path/2015-03-31/functions/{}/invocations".format(
                region_name, lambda_arn
            ),
        )

        self.logger.debug(f"api gateway put integration method response: {integration_response}")

        lambda_client.add_permission(
            FunctionName=fixed_function_name,
            StatementId=f"apigateway-{fixed_function_name}",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn="arn:aws:execute-api:{}:{}:{}/*".format(session.region_name, account_id, api_id),
        )

        deployment_response = api_client.create_deployment(restApiId=api_id, stageName="prod")

        self.logger.debug(f"create api gateway deployment method response: {deployment_response}")
        public_url = "https://{}.execute-api.{}.amazonaws.com/prod/{}".format(api_id, region_name, fixed_function_name)
        self.logger.debug(f"api gateway public url: {public_url}")
        return {"message": f"The lambda API Gateway can be reached here: {public_url}"}

    def _aws_list_lambda_functions(self, aws_access_key_id, aws_secret_access_key, region_name):
        session = boto3.Session(
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        lambda_client = session.client("lambda")
        return [function["FunctionName"] for function in lambda_client.list_functions()["Functions"]]

    def aws_list_lambda_functions(self, region_name):
        return self._aws_list_lambda_functions(self.aws_access_key_id, self.aws_secret_access_key, region_name)

    def create_lambda(self, region_name, lambda_name, lambda_code, function_handler):
        return self._create_lambda(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            region_name,
            lambda_name,
            lambda_code,
            function_handler,
        )

    def delete_lambda(self, region_name, lambda_name):
        return self._delete_lambda(self.aws_access_key_id, self.aws_secret_access_key, region_name, lambda_name)

    def invoke_lambda(self, region_name, lambda_name, payload):
        return self._invoke_lambda(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            region_name,
            lambda_name,
            payload,
        )

    def update_lambda(self, region_name, lambda_name, lambda_code):
        return self._update_lambda(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            region_name,
            lambda_name,
            lambda_code,
        )

    def get_lambda_function_code(self, region_name, lambda_name):
        return self._get_lambda_function_code(
            self.aws_access_key_id, self.aws_secret_access_key, region_name, lambda_name
        )
