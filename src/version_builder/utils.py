import os
import subprocess


def change_dir(path):
    original_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_dir)


class EqualityByValue(object):
    """Override identity eq with a check of the object's underlying fields"""

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Git(object):
    def get_branch_name():
        return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode()

    def get_commit_id():
        return subprocess.check_output(["git", "rev-parse", "--short=7", "HEAD"]).strip().decode()

    def get_description():
        """Output format: <tag>-<commits_since_tag>-g<commit_hash_abbrev>"""
        return subprocess.check_output(["git", "describe", "--tags", "--abbrev=7"]).strip().decode()

    def get_commit_count():
        try:
            return int(subprocess.check_output(["git", "rev-list", "HEAD", "--count"]))
        except subprocess.CalledProcessError:
            # HEAD likely does not exist, meaning no commits
            return 0

    def get_cwd_is_not_empty():
        """Returns true if a directory contains files besides a .git directory"""
        all_entries = os.listdir(os.getcwd())
        nongit_entries = [entry for entry in all_entries if entry != ".git"]
        return len(nongit_entries) != 0

    def get_is_dirty():
        staged_changes = subprocess.call(["git", "diff", "--quiet", "--cached", "--exit-code", "HEAD"]) != 0
        unstaged_changes = subprocess.call(["git", "diff", "--quiet", "--exit-code", "HEAD"]) != 0
        untracked_files = subprocess.call(["git", "ls-files", "--exclude-standard", "--others"]) != ""
        return staged_changes or unstaged_changes or untracked_files
