import os
import unittest
import uuid

from kubernetes import client

from genia.tools.kubernetes_client.namespace import KubernetesNamespace
from genia.tools.kubernetes_client.jobs import KubernetesJobs
from tests.tests_utils import generate_namespace


class TestKubernetesJobs(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_jobs = KubernetesJobs()
        self.api_client_namespace = KubernetesNamespace()
        self.namespace = generate_namespace()
        self.api_client_namespace.create_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def tearDown(self):
        self.api_client_namespace.delete_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        with self.assertRaises(client.rest.ApiException):
            self.api_client_jobs.get_job_status(self.namespace, "42")

        self.assertEqual(self.api_client_jobs.list_namespaced_jobs(self.namespace), [])

        self.assertEqual(
            self.api_client_jobs.create_namespaced_job(
                self.namespace,
                "e2etestjob-1",
                "busybox",
                "busybox:latest",
                "e2etestjob-1-app",
                0,
            ),
            None,
        )
        self.assertEqual(
            self.api_client_jobs.create_namespaced_job(
                self.namespace,
                "e2etestjob-2",
                "busybox",
                "busybox:latest",
                "e2etestjob-2-app",
                3,
            ),
            {"status": 1},
        )

        self.assertGreater(len(self.api_client_jobs.get_job_events(self.namespace, "e2etestjob-2")), 0)

        self.assertEqual(
            self.api_client_jobs.get_job_status(self.namespace, "e2etestjob-2"),
            {
                "active": 1,
                "succeeded": None,
                "failed": None,
                "parallelism": 1,
                "completions": 1,
            },
        )

        self.api_client_jobs.suspend_job(self.namespace, "e2etestjob-2")

        self.assertEqual(
            self.api_client_jobs.get_job_status(self.namespace, "e2etestjob-2"),
            {
                "active": 1,
                "succeeded": None,
                "failed": None,
                "parallelism": 1,
                "completions": 1,
            },
        )

        parallelism = 2
        completions = 2
        self.assertEqual(
            self.api_client_jobs.create_namespaced_job(
                self.namespace,
                "e2etestjob-3",
                "busybox",
                "busybox:latest",
                "e2etestjob-3-app",
                parallelism,
                completions,
            ),
            {"status": 1},
        )

        self.assertEqual(
            self.api_client_jobs.get_job_status(self.namespace, "e2etestjob-3"),
            {
                "active": 1,
                "succeeded": None,
                "failed": None,
                "parallelism": 2,
                "completions": 1,
            },
        )

        self.assertTrue(uuid.UUID(self.api_client_jobs.get_job_controller_uid(self.namespace, "e2etestjob-3")))

        self.api_client_jobs.delete_namespaced_job(self.namespace, "e2etestjob-3")

        with self.assertRaises(client.rest.ApiException):
            self.api_client_jobs.get_job_status(self.namespace, "e2etestjob-3")

        self.assertEqual(
            self.api_client_jobs.list_namespaced_jobs(self.namespace),
            ["e2etestjob-1", "e2etestjob-2"],
        )

        self.assertEqual(
            self.api_client_jobs.get_namespaced_job_logs(self.namespace, "e2etestjob-1"),
            [],
        )


if __name__ == "__main__":
    unittest.main()
