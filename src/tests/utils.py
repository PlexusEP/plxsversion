import os
import subprocess

from version_builder.utils import change_dir


class GitDir:
    def __init__(self, path):
        self.path = path
        self._init_repo()

    def _init_repo(self):
        with change_dir(self.path):
            self._silent_call(["git", "init"])
            self._silent_call(["git", "config", "user.email", "you@example.com"])
            self._silent_call(["git", "config", "user.name", "Your Name"])

    def commit(self):
        self.add_all()
        with change_dir(self.path):
            self._silent_call(["git", "commit", "--allow-empty", "-m", "message"])
            commit_id = self._silent_call(["git", "rev-parse", "--short", "HEAD"]).strip()
            return commit_id

    def add_all(self):
        with change_dir(self.path):
            self._silent_call(["git", "add", "."])

    def _silent_call(self, command):
        with open(os.devnull, "w") as devnull:
            return subprocess.check_output(command, stderr=devnull).decode()

    def create_branch(self, branch_name):
        with change_dir(self.path):
            self._silent_call(["git", "checkout", "-b", branch_name])

    def checkout(self, branch_or_commit_id):
        with change_dir(self.path):
            self._silent_call(["git", "checkout", branch_or_commit_id])

    def tag(self, tag_name):
        with change_dir(self.path):
            self._silent_call(["git", "tag", tag_name])
