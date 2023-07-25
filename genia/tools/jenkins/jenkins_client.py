import os
import logging

import jenkins


class JenkinsClient:
    logger = logging.getLogger(__name__)

    def __init__(self, url=None, username=None, password=None):
        if url == None:
            self.url = os.getenv("JENKINS_URL")
        if username == None:
            self.username = os.getenv("JENKINS_USERNAME")
        if password == None:
            self.password = os.getenv("JENKINS_PASSWORD")
        self.server = jenkins.Jenkins(self.url, username=self.username, password=self.password)
        self.logger.info(self.get_info())

    def get_info(self):
        user = self.server.get_whoami()
        version = self.server.get_version()
        return {"message": f"Hello {user['fullName']} from Jenkins {version}"}

    def get_plugins_info(self):
        return {"message": self.server.get_plugins_info()}

    def build_job(self, job_name):
        self.server.build_job(job_name)
        return {"message": f"succeed to trigger job {job_name}"}

    def get_queue_info(self):
        return {"message": self.server.get_queue_info()}

    def cancel_job(self, job_id):
        self.server.cancel_queue(job_id)
        return {"message": f"succeed to cancel job with id: {job_id}"}
