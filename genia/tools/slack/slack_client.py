import os
import requests
import json
import logging


class SlackClient:
    logger = logging.getLogger(__name__)

    def __init__(self, default_webhook_url=None):
        if default_webhook_url == None:
            self.default_webhook_url = os.getenv("SLACK_DEFAULT_WEBHOOK_URL")

    def send_slack_alert_for_url(self, message, webhook_url=None):
        if not webhook_url:
            webhook_url = self.default_webhook_url

        headers = {"Content-type": "application/json"}
        payload = {"text": message}

        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        self.logger.info(f"slack message sent response: {response}")
        response.raise_for_status()
