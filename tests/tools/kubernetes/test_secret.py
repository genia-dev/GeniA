import os
import unittest

from genia.tools.kubernetes_client.namespace import KubernetesNamespace
from genia.tools.kubernetes_client.secret import KubernetesSecret
from tests.tests_utils import generate_namespace


class TestKubernetesSecret(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_secret = KubernetesSecret()
        self.api_client_namespace = KubernetesNamespace()
        self.namespace = generate_namespace()
        self.api_client_namespace.create_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def tearDown(self):
        self.api_client_namespace.delete_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        self.assertEqual(self.api_client_secret.list_namespaced_secret(self.namespace), None)
        self.assertEqual(self.api_client_secret.check_secret_exists(self.namespace, "42"), False)


if __name__ == "__main__":
    unittest.main()
