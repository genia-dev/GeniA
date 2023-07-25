import os
import re

import unittest

from genia.tools.github_client.github_client import GithubClient

from tests.tests_utils import generate_random_string


class TestGitHub(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.github_client = GithubClient()

    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def test_all(self):
        response = self.github_client.commit_and_create_new_pr(
            owner="genia-dev",
            repository="playground",
            branch=generate_random_string(),
            pull_request_message="New Pull Request by Bot",
            commit_message="PR Hello",
            file_path="main.py",
            commit_content="print('Hello World')",
        )

        pattern = r"Pull request created: https://github\.com/genia-dev/playground/pull/"

        self.assertTrue(re.search(pattern, response["message"]))

        self.assertTrue(len(self.github_client.get_org_repos_names("cncf")) > 100)


if __name__ == "__main__":
    unittest.main()
