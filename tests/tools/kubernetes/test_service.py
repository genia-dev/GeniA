import os
import unittest

from kubernetes import client

from genia.tools.kubernetes_client.namespace import KubernetesNamespace
from genia.tools.kubernetes_client.service import KubernetesService
from tests.tests_utils import generate_namespace


class TestKubernetesService(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_service = KubernetesService()
        self.api_client_namespace = KubernetesNamespace()
        self.namespace = generate_namespace()
        self.api_client_namespace.create_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def tearDown(self):
        self.api_client_namespace.delete_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        with self.assertRaises(client.rest.ApiException):
            self.api_client_service.get_service(self.namespace, "42")

        self.assertNotEqual(self.api_client_service.get_service("kube-system", "kube-dns"), None)
        self.assertGreater(len(self.api_client_service.list_services("kube-system")), 0)


if __name__ == "__main__":
    unittest.main()
