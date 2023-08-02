import logging
import os
from urllib.parse import urlparse

from github import Github, InputGitTreeElement

from genia.agents.adhoc import OpenAIAdhoc
from genia.settings_loader import settings


class GithubClient:
    logger = logging.getLogger(__name__)

    def __init__(self, access_token=None):
        if access_token is None:
            self.access_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        self.adhoc = OpenAIAdhoc()

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

    def get_pr_content(self, repo_name, pull_number):
        g = self.login()
        pull_number = pull_number
        repo = g.get_repo(repo_name)

        pull_request = repo.get_pull(int(pull_number))
        pr_info_str = ""

        pr_info_str += f"PR Title: {pull_request.title}\n"
        pr_info_str += f"PR Description: {pull_request.body}\n\n"

        for commit in pull_request.get_commits():
            pr_info_str += f"Commit message: {commit.commit.message}\n"
            pr_info_str += f"Commit SHA: {commit.sha}\n"
            pr_info_str += f"Commit URL: {commit.url}\n"
            full_commit = repo.get_commit(commit.sha)
            files = full_commit.files
            for file in files:
                pr_info_str += f"File Name: {file.filename}\n"
                pr_info_str += f"Status: {file.status}\n"
                pr_info_str += f"Patch: {file.patch}\n"

        return pr_info_str

    def extract_pr_info(self, github_pr_url):
        parsed_url = urlparse(github_pr_url)
        path_parts = parsed_url.path.split("/")
        owner = path_parts[1]
        repo = path_parts[2]
        pr_number = path_parts[4]

        return owner, repo, pr_number

    def summarize_github_pr_content(self, github_pull_request_url):
        owner, repo, pr_number = self.extract_pr_info(github_pull_request_url)
        self.logger.debug(f"extract_pr_info: {owner} {repo} {pr_number}")
        pr_content = self.get_pr_content(f"{owner}/{repo}", pr_number)

        messages = [
            {"role": "system", "content": settings["github_summarizer_prompt"]["system"]},
            # TODO
            {"role": "user", "content": pr_content[:4096]},
        ]
        return self.adhoc.call_model(messages)
