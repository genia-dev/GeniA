import os
import unittest

from genia.tools.kubernetes_client.pod import KubernetesPod
from genia.tools.kubernetes_client.namespace import KubernetesNamespace
from genia.tools.kubernetes_client.events import KubernetesEvents
from tests.tests_utils import generate_namespace


class TestKubernetesEvents(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_events = KubernetesEvents()
        self.api_client_namespace = KubernetesNamespace()
        self.api_client_pod = KubernetesPod()
        self.namespace = generate_namespace()
        self.api_client_namespace.create_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def tearDown(self):
        self.api_client_namespace.delete_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        self.api_client_pod.create_namespaced_pod(self.namespace, "notexist", "notexist:42")
        self.assertGreater(len(self.api_client_events.list_namespaced_events(self.namespace)), 0)
        self.assertGreater(len(self.api_client_events.list_events_for_all_namespaces()), 0)


if __name__ == "__main__":
    unittest.main()
