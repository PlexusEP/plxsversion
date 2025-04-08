import subprocess
import os
import re
from version_builder.version_info import VersionInfo
from version_builder import utils


class VersionParseError(Exception):
    def __init__(self, version_string):
        self.version_string = version_string

    def __str__(self):
        return "Version not parseable: %s" % self.version_string


def from_git(git_directory):
    return _GitGetter().get_version(git_directory)


def from_file(file_path):
    return _FileGetter().get_version(file_path)


class _Getter(object):
    def __init__(self):
        pass

    def get_version(self, data_source):
        return self.compute_version(data_source)


class _GitGetter(_Getter):
    def compute_version(self, git_directory):
        with utils.ChDir(git_directory):
            try:
                with open(os.devnull, "w") as devnull:
                    version_string = subprocess.check_output(
                        ["git", "describe", "--tags", "--long", "--abbrev=7"], stderr=devnull
                    ).decode()
                return self._parse_git_version(version_string, self._is_cwd_modified_since_commit())
            except subprocess.CalledProcessError:
                # If there is no git tag, then the commits_since_tag returned by git is wrong
                # (because they consider the branch HEAD the tag and there are 0 commits since the branch head).
                # We want to return the total number of commits in the branch if there is no tag.
                total_num_commits = utils.Git.get_cwd_commit_count()
                if total_num_commits > 0:
                    # There is no git tag, but there are commits
                    branch_name = utils.Git.get_cwd_branch_name()
                    commit_id = utils.Git.get_cwd_commit_id()
                    return VersionInfo(
                        tag_name=branch_name,
                        commits_since_tag=total_num_commits,
                        commit_id=commit_id,
                        tag_exists=False,
                        modified_since_commit=self._is_cwd_modified_since_commit(),
                    )
                else:
                    # There are no commits yet
                    branch_name = "HEAD"
                    commit_id = "0"
                    return VersionInfo(
                        tag_name=branch_name,
                        commits_since_tag=total_num_commits,
                        commit_id=commit_id,
                        tag_exists=False,
                        modified_since_commit=utils.Git.get_cwd_is_not_empty(),
                    )

    def _is_cwd_modified_since_commit(self):
        return utils.Git.get_cwd_contains_modified_files() or utils.Git.get_cwd_contains_untracked_files()

    def _parse_git_version(self, git_version_string, modified_since_commit):
        assert isinstance(git_version_string, str)
        matched = re.match(r"^([a-zA-Z0-9\.\-\_/]+)-([0-9]+)-g([0-9a-f]+)$", git_version_string)
        if matched:
            tag = matched.group(1)
            commits_since_tag = int(matched.group(2))
            commit_id = matched.group(3)
            return VersionInfo(
                tag_name=tag,
                commits_since_tag=commits_since_tag,
                commit_id=commit_id,
                tag_exists=True,
                modified_since_commit=modified_since_commit,
            )
        else:
            raise VersionParseError(git_version_string)


class _FileGetter(_Getter):
    def compute_version(self, file_path):
        with open(file_path, "r") as input_file:
            tag = input_file.readline().strip()
            if tag:
                return VersionInfo(
                    tag_name=tag,
                    commits_since_tag=0,
                    commit_id="",
                    tag_exists=True,
                    modified_since_commit=False,
                )
            else:
                raise VersionParseError("empty file")
