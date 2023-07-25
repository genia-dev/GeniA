import os
import time
import unittest

from genia.tools.kubernetes_client.pod import KubernetesPod
from genia.tools.kubernetes_client.namespace import KubernetesNamespace
from tests.tests_utils import generate_namespace
from kubernetes import client


class TestKubernetesPod(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_pod = KubernetesPod()
        self.api_client_namespace = KubernetesNamespace()
        self.namespace = generate_namespace()
        self.api_client_namespace.create_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def tearDown(self):
        self.api_client_namespace.delete_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        with self.assertRaises(client.rest.ApiException):
            self.api_client_pod.delete_namespaced_pod(self.namespace, "42")

        self.assertEqual(self.api_client_pod.list_namespaced_pod(self.namespace), [])
        self.api_client_pod.create_namespaced_pod(self.namespace, "nginx", "nginx:1.14")
        self.assertEqual(len(self.api_client_pod.list_namespaced_pod(self.namespace)), 1)
        self.assertEqual(
            self.api_client_pod.read_namespaced_pod(self.namespace, "nginx")["containers"],
            [{"image": "nginx:1.14", "name": "nginx"}],
        )
        self.assertEqual(
            self.api_client_pod.read_namespaced_pod_resources(self.namespace, "nginx"),
            [{"limits": None, "name": "nginx", "requests": None}],
        )
        self.api_client_pod.patch_namespaced_pod_image(self.namespace, "nginx", "nginx:1.19")
        self.assertEqual(
            self.api_client_pod.read_namespaced_pod(self.namespace, "nginx")["containers"],
            [{"image": "nginx:1.19", "name": "nginx"}],
        )
        self.assertEqual(
            self.api_client_pod.list_namespaced_pods_status(self.namespace, "Failed"),
            [],
        )
        self.api_client_pod.create_namespaced_pod(self.namespace, "notexist", "notexist:42")

        if os.environ.get("PYTHON_E2E_TESTS_WITH_WAIT"):
            time.sleep(2)
            self.assertEqual(
                self.api_client_pod.list_namespaced_pods_status(self.namespace, "Running"),
                ["nginx"],
            )
            self.assertEqual(
                self.api_client_pod.exec_command_in_pod(self.namespace, "nginx", "whoami"),
                "root\n",
            )


if __name__ == "__main__":
    unittest.main()
