import os
import unittest

from genia.tools.kubernetes_client.cronjob import KubernetesCronJob
from genia.tools.kubernetes_client.namespace import KubernetesNamespace
from tests.tests_utils import generate_namespace


class TestKubernetesCronJob(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_cronjob = KubernetesCronJob()
        self.api_client_namespace = KubernetesNamespace()
        self.namespace = generate_namespace()
        self.api_client_namespace.create_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def tearDown(self):
        self.api_client_namespace.delete_namespace(self.namespace)

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        self.assertEqual(
            self.api_client_cronjob.list_enabled_cronjobs_for_namespace(self.namespace),
            [],
        )

        cron_job_name = "test-cronjob"

        self.api_client_cronjob.create_cronjob(
            name=cron_job_name,
            namespace=self.namespace,
            schedule="*/1 * * * *",
            command=["/bin/sh", "-c", "date"],
            image="busybox",
        )

        self.assertEqual(
            len(self.api_client_cronjob.list_suspended_cronjobs_for_namespace(self.namespace)),
            0,
        )
        self.assertEqual(
            len(self.api_client_cronjob.list_disabled_cronjobs_for_namespace(self.namespace)),
            0,
        )
        self.assertEqual(
            len(self.api_client_cronjob.list_enabled_cronjobs_for_namespace(self.namespace)),
            1,
        )

        self.api_client_cronjob.suspend_cronjob(self.namespace, cron_job_name)

        self.assertEqual(
            len(self.api_client_cronjob.list_suspended_cronjobs_for_namespace(self.namespace)),
            1,
        )
        self.assertEqual(
            len(self.api_client_cronjob.list_disabled_cronjobs_for_namespace(self.namespace)),
            0,
        )
        self.assertEqual(
            len(self.api_client_cronjob.list_enabled_cronjobs_for_namespace(self.namespace)),
            1,
        )

        print(self.api_client_cronjob.unsuspend_cronjob(self.namespace, cron_job_name))

        self.assertEqual(
            len(self.api_client_cronjob.list_suspended_cronjobs_for_namespace(self.namespace)),
            0,
        )
        self.assertEqual(
            len(self.api_client_cronjob.list_disabled_cronjobs_for_namespace(self.namespace)),
            0,
        )
        self.assertEqual(
            len(self.api_client_cronjob.list_enabled_cronjobs_for_namespace(self.namespace)),
            1,
        )


if __name__ == "__main__":
    unittest.main()
