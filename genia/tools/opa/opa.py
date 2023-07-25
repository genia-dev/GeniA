import os
import glob
import logging
from opa_client.opa import OpaClient


class OpaClientWrapper:
    logger = logging.getLogger(__name__)

    @staticmethod
    def load_rego_files(path):
        files = glob.glob(os.path.join(path, "*.rego"))
        policies = {}
        for file in files:
            with open(file, "r") as f:
                policies[os.path.basename(file)] = f.read()
        return policies

    def __init__(self):
        self.client = OpaClient()
        self.client.check_connection()

        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(current_dir, "policies")

        policies = OpaClientWrapper.load_rego_files(file_path)

        for key, value in policies.items():
            self.client.update_opa_policy_fromstring(value, key)

        self.logger.debug(self.client.get_policies_list())

    def opa_check_policy_rule(self, input_data, package_path="policy"):
        self.logger.debug(input_data)
        if "input_data" in input_data:
            input_data = input_data["input_data"]
        return self.client.check_policy_rule(input_data, package_path)
