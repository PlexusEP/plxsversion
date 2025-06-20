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
        def _process_git_tag(raw_tag: str) -> str:
            # Strip leading 'v' if present, as SemVer itself doesn't include it.
            # Ensure it's a 'v' followed by a digit to avoid stripping 'v' from non-version tags.
            if raw_tag.startswith("v") and len(raw_tag) > 1 and raw_tag[1].isdigit():
                return raw_tag[1:]
            return raw_tag

        with utils.change_dir(repo_path):
            try:
                repo_description = utils.Git.get_description()
                # Example git describe output: "v1.2.3-alpha-2-g1234567" or "my-custom-tag-0-gabcdef0"
                match = re.match(r"^(.*)-(\d+)-g([0-9a-fA-F]{7,})$", repo_description)
                if match:  # The regex should match standard git describe --long output if a tag exists
                    tag = _process_git_tag(match.group(1))  # group(1) is the tag name part
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
                raise VersionCollectError(msg)  # This case should ideally not be hit with standard git describe output
            except subprocess.CalledProcessError as exc:
                # no tag exists
                total_number_commits = utils.Git.get_commit_count()
                if total_number_commits > 0:
                    # There is no git tag, but there are commits
                    commit_id = utils.Git.get_commit_id()
                    return VersionData(
                        tag="0.0.0-UNTAGGED",  # This is a valid SemVer 2.0.0 pre-release
                        commit_id=commit_id,
                        branch_name=utils.Git.get_branch_name(),
                        is_dirty=utils.Git.get_is_dirty(),
                        commits_since_tag=total_number_commits,
                    )
                msg = "no commits exist"
                raise VersionCollectError(msg) from exc


class _File(_VersionCollector):
    def compute_version(self, file_path: str) -> VersionData:
        def _process_file_tag(raw_tag: str) -> str:
            # Strip leading 'v' if present, ensuring it's a 'v' followed by a digit.
            if raw_tag.startswith("v") and len(raw_tag) > 1 and raw_tag[1].isdigit():
                return raw_tag[1:]
            return raw_tag

        with open(file_path) as input_file:
            tag = _process_file_tag(input_file.readline().strip())
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
