import os
import requests
import unittest

from genia.tools.slack.slack_client import SlackClient


class TestSlackClient(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("PYTHON_E2E_TESTS_WITH_WAIT") != None,
        "Not in e2e test environment",
    )
    def setUp(self):
        self.slack_client = SlackClient()

    @unittest.skipUnless(
        os.environ.get("PYTHON_E2E_TESTS_WITH_WAIT") != None,
        "Not in e2e test environment",
    )
    def test_all(self):
        with self.assertRaises((requests.exceptions.MissingSchema, requests.exceptions.HTTPError)):
            self.slack_client.send_slack_alert_for_url("42", "https://hooks.slack.com/services/XXXX/XXXX/XXXX")

        self.assertEqual(
            self.slack_client.send_slack_alert_for_url(
                "Hello From Python Integration Bot", os.getenv("SLACK_WEBHOOK_URL")
            ),
            None,
        )


if __name__ == "__main__":
    unittest.main()
