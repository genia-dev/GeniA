import os
import unittest

from genia.tools.aws_client.ecs.aws_client_ecs import AWSClientECS


class TestECS(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_ecs = AWSClientECS()

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        region_name = "us-west-2"

        with self.assertRaises(Exception):
            self.api_client_ecs.restart_cluster(region_name, "42")

        self.assertEqual(self.api_client_ecs.list_clusters(region_name), [])


if __name__ == "__main__":
    unittest.main()
