import os
import unittest
import time

from genia.tools.kubernetes_client.deployment import KubernetesDeployment
from genia.tools.kubernetes_client.namespace import KubernetesNamespace
from tests.tests_utils import generate_namespace
from kubernetes import client


class TestKubernetesDeployment(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_deployment = KubernetesDeployment()
        self.api_client_namespace = KubernetesNamespace()
        self.namespace = generate_namespace()
        self.api_client_namespace.create_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def tearDown(self):
        self.api_client_namespace.delete_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        with self.assertRaises(client.rest.ApiException):
            self.assertEqual(self.api_client_deployment.describe_deployment(self.namespace, "42"), [])

        self.api_client_deployment.create_deployment(self.namespace, "nginx", "nginx:latest", 1)

        self.assertEqual(
            self.api_client_deployment.describe_deployment(self.namespace, "nginx"),
            {
                "image": "nginx:latest",
                "name": "nginx",
                "namespace": self.namespace,
                "replicas": 1,
                "resources": {"nginx": {"limits": None, "requests": None}},
            },
        )

        self.api_client_deployment.scale_deployment(self.namespace, "nginx", 2)

        self.assertEqual(
            self.api_client_deployment.describe_deployment(self.namespace, "nginx"),
            {
                "image": "nginx:latest",
                "name": "nginx",
                "namespace": self.namespace,
                "replicas": 2,
                "resources": {"nginx": {"limits": None, "requests": None}},
            },
        )

        self.api_client_deployment.scale_deployment_resources(
            self.namespace, "nginx", "nginx", "100m", "200Mi", "300m", "600Mi"
        )

        self.assertEqual(
            self.api_client_deployment.describe_deployment(self.namespace, "nginx"),
            {
                "image": "nginx:latest",
                "name": "nginx",
                "namespace": self.namespace,
                "replicas": 2,
                "resources": {
                    "nginx": {
                        "limits": {"cpu": "300m", "memory": "600Mi"},
                        "requests": {"cpu": "100m", "memory": "200Mi"},
                    }
                },
            },
        )

        if os.environ.get("PYTHON_E2E_TESTS_WITH_WAIT"):
            time.sleep(5)

            logs_0 = self.api_client_deployment.get_deployment_logs(self.namespace, "nginx", 0)
            self.assertEquals(logs_0[0]["logs"], "")
            logs_10 = self.api_client_deployment.get_deployment_logs(self.namespace, "nginx", 10)
            self.assertGreater(len(logs_10[0]["logs"]), 1)


if __name__ == "__main__":
    unittest.main()
