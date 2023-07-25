import os
import unittest

from genia.tools.opa.opa import OpaClientWrapper
from tests.tests_utils import bypass_pytest_print


class TestOPA(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.opa_client_wrapper = OpaClientWrapper()

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        input = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "frontend"},
            "spec": {
                "containers": [
                    {
                        "name": "app",
                        "image": "images.my-company.example/app:v4",
                        "resources": {"requests": {"memory": "64Mi", "cpu": "250m"}},
                    },
                    {
                        "name": "log",
                        "image": "images.my-company.example/log-aggregator:v6",
                        "resources": {"requests": {"memory": "64Mi", "cpu": "250m"}},
                    },
                ]
            },
        }
        expected = {
            "result": {
                "deny": [
                    "Container 'app' does not have CPU and memory limits defined",
                    "Container 'app' runs as root",
                    "Container 'log' does not have CPU and memory limits defined",
                    "Container 'log' runs as root",
                ]
            }
        }
        self.assertEqual(self.opa_client_wrapper.opa_check_policy_rule(input), expected)


if __name__ == "__main__":
    unittest.main()
