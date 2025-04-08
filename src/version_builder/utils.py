import os
import subprocess

# Use this like
# > with ChDir(my_dir):
# >   do_something()
# Then, the working directory will be set to my_dir, do_something() will be called,
# and the working directory will be set back.


class ChDir(object):
    def __init__(self, directory):
        self.directory = directory

    def __enter__(self):
        self.old_dir = os.getcwd()
        os.chdir(self.directory)

    def __exit__(self, exc_type, value, traceback):
        os.chdir(self.old_dir)


class EqualityMixin(object):
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class Git(object):
    def get_cwd_branch_name():
        return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode()

    def get_cwd_commit_id():
        return subprocess.check_output(["git", "log", "--format=%h", "-n", "1"]).strip().decode()

    def get_cwd_commit_count():
        try:
            with open(os.devnull, "w") as devnull:
                return int(subprocess.check_output(["git", "rev-list", "HEAD", "--count"], stderr=devnull))
        except subprocess.CalledProcessError:
            return 0

    def get_cwd_is_not_empty():
        all_entries = os.listdir(os.getcwd())
        nongit_entries = [entry for entry in all_entries if entry != ".git"]
        return len(nongit_entries) != 0

    def get_cwd_contains_untracked_files():
        return subprocess.check_output(["git", "ls-files", "--exclude-standard", "--others"]).strip().decode() != ""

    def get_cwd_contains_modified_files():
        # Usually we'd like to use "git diff-index" here.
        # But there seems to be a bug that when we run "chmod 755 file" on a file that already has 755 and is committed to
        # git as such, the next run of "git diff-index" will show it as a difference. "git diff" seams to work
        return 0 != (subprocess.call(["git", "diff", "--exit-code", "--quiet", "HEAD"])) or (
            0 != subprocess.call(["git", "diff", "--cached", "--exit-code", "--quiet", "HEAD"])
        )
