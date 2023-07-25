import os
import unittest

from genia.tools.aws_client.cloudtrail.aws_client_cloudtrail import AWSClientCloudTrail


class TestCloudTrail(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_cloudtrail = AWSClientCloudTrail()

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        self.assertEqual(
            self.api_client_cloudtrail.list_users_in_group_more_than_x_time("notexist", 1),
            [],
        )


if __name__ == "__main__":
    unittest.main()
