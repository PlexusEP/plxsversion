import shutil
import subprocess
import random
import os
import string
from tempfile import mkdtemp, NamedTemporaryFile
from version_builder.utils import change_dir


class TempDir(object):
    def __enter__(self):
        self.path = mkdtemp()
        return self.path

    def __exit__(self, exc_type, value, tb):
        shutil.rmtree(self.path)


class TempFile(object):
    def __init__(self, suffix=""):
        self.suffix = suffix

    def __enter__(self):
        f = NamedTemporaryFile(suffix=self.suffix)
        f.close()  # This also deletes the file
        self.filename = f.name
        return f.name

    def __exit__(self, exc_type, value, tb):
        if os.path.isfile(self.filename):
            os.remove(self.filename)


class GitDir(object):
    def __enter__(self):
        self.path = mkdtemp()
        self._setup_git()
        return self

    def __exit__(self, exc_type, value, traceback):
        shutil.rmtree(self.path)

    def _setup_git(self):
        with change_dir(self.path):
            self._silent_call(["git", "init"])
            self._silent_call(["git", "config", "user.email", "you@example.com"])
            self._silent_call(["git", "config", "user.name", "Your Name"])

    def create_git_commit(self):
        self.add_tracked_file()
        with change_dir(self.path):
            self._silent_call(["git", "commit", "-m", "message"])
            commit_id = self._silent_call(["git", "rev-parse", "--short", "HEAD"]).strip()
            return commit_id

    def add_untracked_file(self):
        filename = self._random_string(10)
        with change_dir(self.path):
            self._silent_call(["touch", filename])
            return filename

    def add_tracked_file(self):
        filename = self.add_untracked_file()
        with change_dir(self.path):
            self._silent_call(["git", "add", filename])
            return filename

    def modify_file(self, filename):
        content = self._random_string(10)
        with change_dir(self.path):
            with open(filename, "w") as file:
                file.write(content)

    def _random_string(self, length):
        return "".join(random.choice(string.ascii_lowercase) for _ in range(length))

    def _silent_call(self, command):
        with open(os.devnull, "w") as devnull:
            return subprocess.check_output(command, stderr=devnull).decode()

    def create_git_branch(self, branch_name):
        with change_dir(self.path):
            self._silent_call(["git", "checkout", "-b", branch_name])

    def switch_git_branch(self, branch_name):
        with change_dir(self.path):
            self._silent_call(["git", "checkout", branch_name])

    def checkout_git_commit(self, commit_id):
        with change_dir(self.path):
            self._silent_call(["git", "checkout", commit_id])

    def create_git_tag(self, tag_name):
        with change_dir(self.path):
            self._silent_call(["git", "tag", tag_name])
