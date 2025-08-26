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

    def _get_valid_semver_tags_on_commit(self, commit_hash: str) -> list[str]:
        """Return a list of valid SemVer tags pointing at a specific commit."""
        try:
            tags_raw = subprocess.check_output(  # noqa: S603
                ["git", "tag", "--points-at", commit_hash], stderr=subprocess.PIPE
            ).decode()
            tags = [tag for tag in tags_raw.strip().split("\n") if tag]
            return [tag for tag in tags if self._is_valid_semver(tag)]
        except subprocess.CalledProcessError:
            return []

    def _find_version_from_history(self, head_commit_id_full: str) -> tuple[str, int] | None:
        """
        Search git history for the most recent, unambiguous SemVer tag on an ancestor commit.

        Returns (tag, commits_since) or None if no suitable tag is found.
        """
        try:
            all_tags_raw = subprocess.check_output(  # noqa: S603
                ["git", "for-each-ref", "--sort=-creatordate", "--format", "%(refname:short)", "refs/tags"],
                stderr=subprocess.PIPE,
            ).decode()
            all_tags = [tag for tag in all_tags_raw.strip().split("\n") if tag]
        except subprocess.CalledProcessError:
            return None

        for tag_name in all_tags:
            if self._is_valid_semver(tag_name):
                # Check if it's an ancestor
                is_ancestor_proc = subprocess.run(  # noqa: S603
                    ["git", "merge-base", "--is-ancestor", tag_name, "HEAD"], capture_output=True, check=False
                )
                if is_ancestor_proc.returncode == 0:
                    # Found a candidate. Now check for ambiguity on that ancestor commit.
                    tag_commit_id_full = (
                        subprocess.check_output(["git", "rev-parse", tag_name]).decode().strip()  # noqa: S603
                    )
                    valid_semver_tags_on_ancestor = self._get_valid_semver_tags_on_commit(tag_commit_id_full)

                    if len(valid_semver_tags_on_ancestor) > 1:
                        short_tag_commit_id = (
                            subprocess.check_output(["git", "rev-parse", "--short=7", tag_name]).decode().strip()  # noqa: S603
                        )
                        if tag_commit_id_full == head_commit_id_full:
                            location_str = f"commit {short_tag_commit_id}"
                        else:
                            location_str = f"ancestor commit {short_tag_commit_id}"
                        msg = (
                            f"multiple valid SemVer tags on {location_str}: {', '.join(valid_semver_tags_on_ancestor)}"
                        )
                        raise VersionCollectError(msg)

                    # This is our tag.
                    count_raw = subprocess.check_output(  # noqa: S603
                        ["git", "rev-list", "--count", f"{tag_name}..HEAD"]
                    ).decode()
                    commits_since_tag = int(count_raw.strip())

                    processed_tag = self._process_tag(tag_name)
                    return processed_tag, commits_since_tag
        return None

    def _get_fallback_version(self, commit_id: str) -> VersionData:
        """Return the fallback version when no valid SemVer tags are found."""
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

            # Search history for the most recent, unambiguous SemVer tag.
            # This handles tags on the current commit as well as on ancestors.
            tag_info = self._find_version_from_history(commit_id_full)
            if tag_info:
                tag, commits_since_tag = tag_info
                return VersionData(
                    tag=tag,
                    commit_id=commit_id,
                    branch_name=utils.Git.get_branch_name(),
                    is_dirty=utils.Git.get_is_dirty(),
                    commits_since_tag=commits_since_tag,
                )

            # No valid tags found, use fallback.
            return self._get_fallback_version(commit_id)


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
