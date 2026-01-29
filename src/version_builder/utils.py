import os
import subprocess
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def change_dir(path: str) -> None:
    original_dir = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_dir)


class EqualityByValue:
    """Override identity eq with a check of the object's underlying fields."""

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> bool:
        return hash(self.name)


class Git:
    @staticmethod
    def get_branch_name() -> str:
        # No user input is passed to subprocess calls
        return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode()

    @staticmethod
    def get_commit_id(*, short: bool = True) -> str:
        # No user input is passed to subprocess calls
        command = ["git", "rev-parse"]
        if short:
            command.append("--short=7")
        command.append("HEAD")
        return subprocess.check_output(command).strip().decode()  # noqa: S603

    @staticmethod
    def get_description() -> str:
        """Output format: <tag>-<commits_since_tag>-g<commit_hash_abbrev>."""
        # No user input is passed to subprocess calls
        return subprocess.check_output(["git", "describe", "--tags", "--abbrev=7", "--long"]).strip().decode()

    @staticmethod
    def get_commit_count() -> int:
        try:
            # No user input is passed to subprocess calls
            return int(subprocess.check_output(["git", "rev-list", "HEAD", "--count"]))
        except subprocess.CalledProcessError:
            # HEAD likely does not exist, meaning no commits
            return 0

    @staticmethod
    def get_cwd_is_not_empty() -> bool:
        """Return true if a directory contains files besides a .git directory."""
        # listdir offers a simpler and more readable way to collect all files in a directory
        all_entries = os.listdir(Path.cwd())  # noqa: PTH208
        nongit_entries = [entry for entry in all_entries if entry != ".git"]
        return len(nongit_entries) != 0

    @staticmethod
    def get_is_dirty() -> bool:
        # No user input is passed to subprocess calls
        staged_changes = subprocess.call(["git", "diff", "--quiet", "--cached", "--exit-code", "HEAD"]) != 0
        unstaged_changes = subprocess.call(["git", "diff", "--quiet", "--exit-code", "HEAD"]) != 0
        untracked_files = subprocess.check_output(["git", "ls-files", "--exclude-standard", "--others"]).decode() != ""
        return staged_changes or unstaged_changes or untracked_files
