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
    # Official SemVer 2.0.0 regex: https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
    _SEMVER_REGEX = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"  # noqa: E501

    def __init__(
        self, tag: str, commit_id: str, branch_name: str, *, is_dirty: bool = False, commits_since_tag: int = 0
    ) -> None:
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

        match = re.match(self._SEMVER_REGEX, tag)
        if not match:
            msg = "invalid SemVer 2.0.0 format"
            raise VersionParseError(msg, tag)

        self.tag = tag
        self.commit_id = commit_id
        self.branch_name = branch_name
        self.is_dirty = is_dirty
        self.commits_since_tag = commits_since_tag

        self.major = int(match.group(1))
        self.minor = int(match.group(2))
        self.patch = int(match.group(3))
        self.components = [self.major, self.minor, self.patch]
        self.prerelease = match.group(4) or ""  # Pre-release identifiers (e.g., "alpha.1")
        self.buildmetadata_from_tag = match.group(5) or ""  # Build metadata from tag (e.g., "build.123")

        self.time = ""
        self._set_qualified_version()
        self.is_development_build = self.is_dirty or (commits_since_tag > 0)

    def set_time(self) -> None:
        self.time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    def _set_qualified_version(self) -> None:
        core_version = f"{self.major}.{self.minor}.{self.patch}"

        qualified_version_str = core_version
        if self.prerelease:
            qualified_version_str += f"-{self.prerelease}"

        # Construct build metadata
        # Starts with metadata from the tag, then appends build-time information.
        build_metadata_elements = []
        if self.buildmetadata_from_tag:
            build_metadata_elements.append(self.buildmetadata_from_tag)

        build_time_metadata_sub_elements = []
        if self.commits_since_tag > 0:
            # SemVer build metadata identifiers are alphanumeric and hyphens.
            # Git short hash (commit_id) is typically hex, which is fine.
            build_time_metadata_sub_elements.append(f"dev.{self.commits_since_tag}.sha.{self.commit_id}")
        else:
            # If on a tag (commits_since_tag is 0), include just the commit hash.
            build_time_metadata_sub_elements.append(f"sha.{self.commit_id}")
        if self.is_dirty:
            build_time_metadata_sub_elements.append("dirty")

        if build_time_metadata_sub_elements:
            build_metadata_elements.append(".".join(build_time_metadata_sub_elements))

        self.full_build_metadata = ".".join(build_metadata_elements)

        if self.full_build_metadata:
            qualified_version_str += f"+{self.full_build_metadata}"

        self.qualified_version = qualified_version_str
