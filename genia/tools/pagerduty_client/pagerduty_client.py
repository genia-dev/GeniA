import os
import logging
import requests
import json
import pdpyras


class PagerDutyClient:
    logger = logging.getLogger(__name__)

    def __init__(self, api_key=None):
        if api_key == None:
            self.pd_api_key = os.getenv("PAGERDUTY_API_KEY")
        self.pd_from = os.getenv("PAGERDUTY_FROM")
        self.session = pdpyras.APISession(self.pd_api_key, self.pd_from)

    def get_oncall(self):
        oncalls = self.session.list_all("oncalls", params={})
        self.logger.debug(f"oncalls: {oncalls}")
        first_oncall_email = self.session.jget(f"/users/{oncalls[0]['user']['id']}")["user"]["email"]
        self.logger.debug(f"first oncall email: {first_oncall_email}")
        return first_oncall_email

    def trigger_incident(self, incident_title, service_id):
        url = "https://api.pagerduty.com/incidents"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Authorization": "Token token={token}".format(token=self.pd_api_key),
            "From": self.pd_from,
        }

        payload = {
            "incident": {
                "type": "incident",
                "title": incident_title,
                "service": {"id": service_id, "type": "service_reference"},
                "body": {"type": "incident_body", "details": incident_title},
            }
        }

        r = requests.post(url, headers=headers, data=json.dumps(payload))

        self.logger.debug(f"PagerDuty trigger_incident status code: {r.status_code}")
        self.logger.debug(f"PagerDuty trigger_incident response: {r.json()}")

        r.raise_for_status()

        return {"message": f"Succeed to trigger incident"}

    # TODO PagerDuty has bug in that functionallity - missing 'Content-Type': 'application/json' which cause error `params must be a Hash`
    # def trigger_incident(self, incident_title):
    #     DEFAULT_SERVICE_ID = "P552O9Q"
    #     incident = {
    #         "type": "incident",
    #         "title": incident_title,
    #         "service": {
    #             "id": DEFAULT_SERVICE_ID,
    #             "type": "service_reference"
    #         },
    #         "body": {
    #             "type": "incident_body",
    #             "details": incident_title
    #         }
    #     }
    #
    #     self.session.rpost("incidents",json=[incident])

    def list_services(self):
        return self.session.list_all("services", params={})
