import os
import time
import requests
import unittest

from genia.tools.argo.argo_client import ArgoClient


class TestArgo(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.argo_client = ArgoClient()

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        with self.assertRaises(requests.exceptions.HTTPError):
            self.argo_client.get_workflow("argocd", "42")

        self.argo_client.get_version()
        self.argo_client.get_applications()
        self.argo_client.get_clusters()
        # self.argo_client.get_applications_logs_by_app("guestbook")

        name = "production"
        namespace = "argocd"
        container_image = "geniadev/frontend-production:latest"
        generated_workflow = self.argo_client.submit_workflow_inner(name, namespace, container_image)

        if os.environ.get("PYTHON_E2E_TESTS_WITH_WAIT"):
            time.sleep(7)
            workflow = self.argo_client.get_workflow(namespace, generated_workflow)
            del workflow["creation_timestamp"]
            del workflow["name"]

            self.assertEqual(
                workflow,
                {
                    "namespace": namespace,
                    "status_phase": "Running",
                    "container_image": container_image,
                },
            )
            self.assertTrue(len(self.argo_client.get_workflow_log(namespace, generated_workflow)) > 0)


if __name__ == "__main__":
    unittest.main()
