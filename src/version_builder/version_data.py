import re
from datetime import datetime, timezone

from version_builder.utils import EqualityByValue


class VersionParseError(Exception):
    def __init__(self, root_cause: str, version_input: str) -> None:
        self.root_cause = root_cause
        self.version_input = version_input

    def __str__(self) -> str:
        return f"Version not parseable because {self.root_cause:s}. Input: {self.version_input:s}"


class VersionData(EqualityByValue):
    def __init__(
        self, tag: str, commit_id: str, branch_name: str, *, is_dirty: bool = False, commits_since_tag: int = 0
    ) -> None:
        self._version_format_regex = r"^v?([0-9]+(?:\.[0-9]+){2}){1}(?:-([A-Za-z0-9\_/]+))?$"

        if not isinstance(tag, str):
            msg = "tag is not str type"
            raise TypeError(msg)
        if not isinstance(commit_id, str):
            msg = "commit_id is not str type"
            raise TypeError(msg)
        if not isinstance(branch_name, str):
            msg = "branch_name is not str type"
            raise TypeError(msg)
        if not isinstance(is_dirty, bool):
            msg = "is_dirty is not bool type"
            raise TypeError(msg)
        if not isinstance(commits_since_tag, int):
            msg = "commits_since_tag is not int type"
            raise TypeError(msg)

        if not tag:
            msg = "empty tag input"
            raise VersionParseError(msg, tag)

        if not re.match(self._version_format_regex, tag, re.IGNORECASE):
            msg = "invalid format"
            raise VersionParseError(msg, tag)

        self.tag = tag
        self.commit_id = commit_id
        self.branch_name = branch_name
        self.is_dirty = is_dirty
        self.commits_since_tag = commits_since_tag
        self.components = []
        self.descriptor = ""
        self.time = ""
        self._parse_tag()
        self._set_qualified_version()
        self.is_development_build = self.is_dirty or (commits_since_tag > 0)

    def set_time(self) -> None:
        self.time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    def _parse_tag(self) -> None:
        match = re.match(self._version_format_regex, self.tag, re.IGNORECASE)
        if match:
            self.components = list(map(int, match.group(1).split(".")))
            if match.group(2) is not None:
                self.descriptor = match.group(2)

    def _set_qualified_version(self) -> None:
        computed_version = self.tag
        if self.commits_since_tag > 0:
            computed_version += f".rev{self.commit_id:s}+{self.commits_since_tag:d}commits"
        if self.is_dirty:
            computed_version += "-dirty"
        self.qualified_version = computed_version
