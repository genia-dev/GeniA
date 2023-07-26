import os
import unittest

from genia.tools.aws_client.lambdas.aws_client_lambda import AWSClientLambda
from tests.tests_utils import generate_random_string


class TestLambda(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_lambda = AWSClientLambda()

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        region_name = "us-west-2"
        with self.assertRaises(Exception):
            self.api_client_lambda.invoke_lambda(region_name, "42", '{"number": "1"}')

        if os.environ.get("PYTHON_E2E_TESTS_WITH_WAIT"):
            lambda_code = """
        def lambda_handler(event, context):
            number = event['number']
            if number % 2 == 0:
                return {
                    'StatusCode': 200,
                    'isEven': True
                }
            else:
                return {
                    'StatusCode': 200,
                    'isEven': False
                }
            return lambda_response
        """

            lambda_code_update = """
        def lambda_handler(event, context):
                return {
                    'StatusCode': 200,
                    'isEven': True
                }
        """

            function_name = generate_random_string()
            self.api_client_lambda.create_lambda(region_name, function_name, lambda_code, "lambda_handler")
            self.api_client_lambda.invoke_lambda(region_name, function_name, '{"number": "2"}')
            self.api_client_lambda.get_lambda_function_code(region_name, function_name)
            self.api_client_lambda.update_lambda(region_name, function_name, lambda_code_update)
            self.api_client_lambda.invoke_lambda(region_name, function_name, "{}")
            self.api_client_lambda.aws_list_lambda_functions(region_name)
            self.api_client_lambda.delete_lambda(region_name, function_name)


if __name__ == "__main__":
    unittest.main()
