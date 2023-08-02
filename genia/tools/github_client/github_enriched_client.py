import logging

from genia.tools.github_client.github_client import GithubClient


class GithubEnrichedClient(GithubClient):
    logger = logging.getLogger(__name__)

    def create_new_repo(self, new_repo_name: str):
        # Create a GitHub instance
        g = self.login()
        # Create a new repository
        repo = g.get_user().create_repo(new_repo_name)
        # Print the repository details
        result = "Repository {} created successfully on url: {}", repo.name, repo.html_url
        self.logger.debug(result)
        return result
