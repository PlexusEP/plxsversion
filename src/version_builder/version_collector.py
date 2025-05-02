import re
import subprocess
from pathlib import Path

from version_builder import utils
from version_builder.version_data import VersionData


def from_git(git_directory: str) -> VersionData:
    return _Git().get_version(git_directory)


def from_file(file_path: str) -> VersionData:
    return _File().get_version(file_path)


class VersionCollectError(Exception):
    def __init__(self, root_cause: str) -> None:
        self.root_cause = root_cause

    def __str__(self) -> str:
        return f"Could not get version because {self.root_cause:s}. "


class _VersionCollector:
    def __init__(self) -> None:
        pass

    def get_version(self, data_source: str) -> VersionData:
        return self.compute_version(data_source)


class _Git(_VersionCollector):
    def compute_version(self, repo_path: str) -> VersionData:
        with utils.change_dir(repo_path):
            try:
                repo_description = utils.Git.get_description()
                match = re.match(r"([a-zA-Z0-9\.]*-?[a-zA-Z0-9\_]*)-([0-9]*)-g([a-zA-Z0-9]*)", repo_description)
                if match:
                    tag = match.group(1)
                    commits_since_tag = int(match.group(2))
                    commit_id = match.group(3)
                    return VersionData(
                        tag=tag,
                        commit_id=commit_id,
                        branch_name=utils.Git.get_branch_name(),
                        is_dirty=utils.Git.get_is_dirty(),
                        commits_since_tag=commits_since_tag,
                    )
                msg = f'unexpected git describe output "{repo_description:s}"'
                raise VersionCollectError(msg)
            except subprocess.CalledProcessError as exc:
                # no tag exists
                total_number_commits = utils.Git.get_commit_count()
                if total_number_commits > 0:
                    # There is no git tag, but there are commits
                    commit_id = utils.Git.get_commit_id()
                    return VersionData(
                        tag="0.0.0-UNTAGGED",
                        commit_id=commit_id,
                        branch_name=utils.Git.get_branch_name(),
                        is_dirty=utils.Git.get_is_dirty(),
                        commits_since_tag=total_number_commits,
                    )
                msg = "no commits exist"
                raise VersionCollectError(msg) from exc


class _File(_VersionCollector):
    def compute_version(self, file_path: str) -> VersionData:
        with open(file_path) as input_file:
            tag = input_file.readline().strip()
            if tag:
                with utils.change_dir(Path(file_path).parent):
                    # While the tag comes from a file, we assume all projects use git
                    try:
                        return VersionData(
                            tag=tag,
                            commit_id=utils.Git.get_commit_id(),
                            branch_name=utils.Git.get_branch_name(),
                            is_dirty=utils.Git.get_is_dirty(),
                        )
                    except subprocess.CalledProcessError as exc:
                        msg = "input file not in git repo"
                        raise VersionCollectError(msg) from exc
            else:
                msg = "empty file"
                raise VersionCollectError(msg)
