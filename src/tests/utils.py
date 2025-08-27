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
            return self._silent_call(["git", "rev-parse", "--short=7", "HEAD"]).strip()

    def add_all(self):
        with change_dir(self.path):
            self._silent_call(["git", "add", "."])

    def _silent_call(self, command):
        with open(os.devnull, "w") as devnull:
            # Private helper to unit testing should not be used outside of trusted context
            return subprocess.check_output(command, stderr=devnull).decode()

    # This performs a checkout of the new branch as well
    def create_branch(self, branch_name):
        with change_dir(self.path):
            self._silent_call(["git", "checkout", "-b", branch_name])

    def checkout(self, branch_or_commit_id):
        with change_dir(self.path):
            self._silent_call(["git", "checkout", branch_or_commit_id])

    def tag(self, tag_name, commit_id=None):
        with change_dir(self.path):
            command = ["git", "tag", tag_name]
            if commit_id:
                command.append(commit_id)
            self._silent_call(command)
