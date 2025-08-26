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

    def _process_tag(self, raw_tag: str) -> str:
        # Strip leading 'v' if present, as SemVer itself doesn't include it.
        # Ensure it's a 'v' followed by a digit to avoid stripping 'v' from non-version tags.
        if raw_tag.startswith("v") and len(raw_tag) > 1 and raw_tag[1].isdigit():
            return raw_tag[1:]
        return raw_tag


class _Git(_VersionCollector):
    # Official SemVer 2.0.0 regex from version_data.py
    _SEMVER_REGEX = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"  # noqa: E501

    def _is_valid_semver(self, tag: str) -> bool:
        processed_tag = self._process_tag(tag)
        return re.match(self._SEMVER_REGEX, processed_tag) is not None

    def compute_version(self, repo_path: str) -> VersionData:
        with utils.change_dir(repo_path):
            try:
                if utils.Git.get_commit_count() == 0:
                    msg = "no commits exist"
                    raise VersionCollectError(msg)
            except subprocess.CalledProcessError as exc:
                msg = "not a git repository"
                raise VersionCollectError(msg) from exc

            commit_id = utils.Git.get_commit_id()
            commit_id_full = utils.Git.get_commit_id(short=False)

            # Rule 2: check for multiple valid semver tags on current commit
            try:
                tags_on_commit_raw = subprocess.check_output(  # noqa: S603
                    ["git", "tag", "--points-at", commit_id_full], stderr=subprocess.PIPE
                ).decode()
                tags_on_commit = [tag for tag in tags_on_commit_raw.strip().split("\n") if tag]
            except subprocess.CalledProcessError:
                tags_on_commit = []

            valid_semver_tags = [tag for tag in tags_on_commit if self._is_valid_semver(tag)]

            if len(valid_semver_tags) > 1:
                msg = f"multiple valid SemVer tags on commit {commit_id}: {', '.join(valid_semver_tags)}"
                raise VersionCollectError(msg)

            if len(valid_semver_tags) == 1:
                # Exact match on current commit
                tag = self._process_tag(valid_semver_tags[0])
                return VersionData(
                    tag=tag,
                    commit_id=commit_id,
                    branch_name=utils.Git.get_branch_name(),
                    is_dirty=utils.Git.get_is_dirty(),
                    commits_since_tag=0,
                )

            # Rule 1: No valid semver tag on current commit, search history.
            try:
                all_tags_raw = subprocess.check_output(  # noqa: S603
                    ["git", "for-each-ref", "--sort=-creatordate", "--format", "%(refname:short)", "refs/tags"],
                    stderr=subprocess.PIPE,
                ).decode()
                all_tags = [tag for tag in all_tags_raw.strip().split("\n") if tag]
            except subprocess.CalledProcessError:
                all_tags = []

            for tag_name in all_tags:
                if self._is_valid_semver(tag_name):
                    # Check if it's an ancestor
                    is_ancestor_proc = subprocess.run(  # noqa: S603
                        ["git", "merge-base", "--is-ancestor", tag_name, "HEAD"], capture_output=True, check=False
                    )
                    if is_ancestor_proc.returncode == 0:
                        # Found the most recent valid semver tag in history.

                        # Check for ambiguity on the tagged ancestor commit
                        tag_commit_id_full = (
                            subprocess.check_output(["git", "rev-parse", tag_name]).decode().strip()  # noqa: S603
                        )
                        try:
                            tags_on_commit_raw = subprocess.check_output(  # noqa: S603
                                ["git", "tag", "--points-at", tag_commit_id_full], stderr=subprocess.PIPE
                            ).decode()
                            tags_on_commit = [tag for tag in tags_on_commit_raw.strip().split("\n") if tag]
                        except subprocess.CalledProcessError:
                            tags_on_commit = []

                        valid_semver_tags_on_ancestor = [tag for tag in tags_on_commit if self._is_valid_semver(tag)]

                        if len(valid_semver_tags_on_ancestor) > 1:
                            short_tag_commit_id = (
                                subprocess.check_output(["git", "rev-parse", "--short=7", tag_name]).decode().strip()  # noqa: S603
                            )
                            msg = f"multiple valid SemVer tags on ancestor commit {short_tag_commit_id}: {', '.join(valid_semver_tags_on_ancestor)}"  # noqa: E501
                            raise VersionCollectError(msg)

                        count_raw = subprocess.check_output(  # noqa: S603
                            ["git", "rev-list", "--count", f"{tag_name}..HEAD"]
                        ).decode()
                        commits_since_tag = int(count_raw.strip())

                        tag = self._process_tag(tag_name)
                        return VersionData(
                            tag=tag,
                            commit_id=commit_id,
                            branch_name=utils.Git.get_branch_name(),
                            is_dirty=utils.Git.get_is_dirty(),
                            commits_since_tag=commits_since_tag,
                        )

            # Rule 3: No valid semver tags found in ancestry.
            # Intentional print for user status notification
            print("No valid SemVer tags found in git history. Using '0.0.0-UNTAGGED'.")  # noqa: T201
            total_number_commits = utils.Git.get_commit_count()
            return VersionData(
                tag="0.0.0-UNTAGGED",
                commit_id=commit_id,
                branch_name=utils.Git.get_branch_name(),
                is_dirty=utils.Git.get_is_dirty(),
                commits_since_tag=total_number_commits,
            )


class _File(_VersionCollector):
    def compute_version(self, file_path: str) -> VersionData:
        with open(file_path) as input_file:
            tag = self._process_tag(input_file.readline().strip())
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
