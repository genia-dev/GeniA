import os
import unittest

from genia.tools.aws_client.iam.aws_client_iam import AWSClientIAM


class TestIAM(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_iam = AWSClientIAM()

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        self.assertEqual(self.api_client_iam.list_users_in_group("production-shift-group"), [])
        self.assertEqual(
            self.api_client_iam.add_user_to_group("myawesometestuser", "production-shift-group"),
            None,
        )
        self.assertEqual(
            self.api_client_iam.list_users_in_group("production-shift-group"),
            ["myawesometestuser"],
        )
        self.assertEqual(
            self.api_client_iam.remove_user_from_group("myawesometestuser", "production-shift-group"),
            None,
        )
        self.assertEqual(self.api_client_iam.list_users_in_group("production-shift-group"), [])


if __name__ == "__main__":
    unittest.main()
