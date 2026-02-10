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
        self.cargo_version = ""

    def set_time(self) -> None:
        self.time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    def set_cargo_version(self, cargo_version: str) -> None:
        self.cargo_version = cargo_version

    def _set_qualified_version(self) -> None:
        core_version = f"{self.major}.{self.minor}.{self.patch}"
        version_parts = [core_version]
        if self.prerelease:
            version_parts.append(f"-{self.prerelease}")

        # Construct build metadata
        # Build metadata is a series of dot-separated identifiers.
        # We collect all identifiers in a list and then join them.
        metadata_identifiers = []
        if self.buildmetadata_from_tag:
            metadata_identifiers.extend(self.buildmetadata_from_tag.split("."))

        if self.commits_since_tag > 0:
            metadata_identifiers.extend(["dev", str(self.commits_since_tag), "sha", self.commit_id])
        else:
            metadata_identifiers.extend(["sha", self.commit_id])

        if self.is_dirty:
            metadata_identifiers.append("dirty")

        self.full_build_metadata = ".".join(metadata_identifiers)

        if self.full_build_metadata:
            version_parts.append(f"+{self.full_build_metadata}")

        self.qualified_version = "".join(version_parts)
