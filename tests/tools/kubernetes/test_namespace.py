import os
import unittest

from genia.tools.kubernetes_client.namespace import KubernetesNamespace
from tests.tests_utils import generate_namespace
from kubernetes import client


class TestKubernetesNamespace(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_namespace = KubernetesNamespace()
        self.namespace = generate_namespace()
        self.api_client_namespace.create_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def tearDown(self):
        try:
            self.api_client_namespace.delete_namespace(self.namespace)
        except Exception as e:
            pass

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        with self.assertRaises(client.rest.ApiException):
            self.api_client_namespace.get_namespace("42")

        self.assertEqual(
            self.api_client_namespace.get_namespace(self.namespace),
            {"name": self.namespace, "status": "Active"},
        )

        namespaces = self.api_client_namespace.list_namespaces()
        self.assertTrue(self.namespace in namespaces)
        self.assertTrue("42" not in namespaces)

        self.api_client_namespace.delete_namespace(self.namespace)

        namespaces = self.api_client_namespace.list_namespaces()

        self.assertTrue(self.namespace not in namespaces)


if __name__ == "__main__":
    unittest.main()
