import os
import logging
from github import Github, InputGitTreeElement


class GithubClient:
    logger = logging.getLogger(__name__)

    def __init__(self, access_token=None):
        if access_token == None:
            self.access_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    def get_token(self):
        return self.access_token

    def get_orgprefix(self, org):
        return org + "/"

    def login(self) -> Github:
        return Github(self.get_token())

    def get_org_repos_names(self, org=None):
        repos = [repo.name for repo in self.login().get_organization(org).get_repos()]
        return sorted(repos, key=lambda x: x.lower())

    def commit_and_create_new_pr(
        self,
        owner,
        repository,
        branch,
        pull_request_message,
        commit_message,
        file_path,
        commit_content,
    ):
        gh = self.login()
        repo = gh.get_repo("{owner}/{repository}".format(owner=owner, repository=repository))
        sb = repo.get_branch("main")
        tree = repo.create_git_tree([InputGitTreeElement(file_path, "100644", "blob", commit_content)])
        parent = repo.get_git_commit(sb.commit.sha)
        commit = repo.create_git_commit("Commit message", tree, [parent])
        repo.create_git_ref("refs/heads/{branch}".format(branch=branch), commit.sha)
        pr = repo.create_pull(title=pull_request_message, body=commit_message, base="main", head=branch)
        self.logger.debug(pr)
        return {"message": f"Pull request created: {pr.html_url}"}
