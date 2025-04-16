from version_builder.utils import EqualityByValue
import re


class VersionParseError(Exception):
    def __init__(self, root_cause, version_input):
        self.root_cause = root_cause
        self.version_input = version_input

    def __str__(self):
        return "Version not parseable because %s. Input: %s" % (self.root_cause, self.version_input)


class VersionData(EqualityByValue):
    def __init__(self, tag, commit_id, is_dirty, commits_since_tag=0):
        self._version_format_regex = r"^v?([0-9]+(?:\.[0-9]+){2}){1}(?:-([A-Za-z0-9\_/]+))?$"

        assert isinstance(tag, str)
        assert isinstance(commit_id, str)
        assert isinstance(is_dirty, bool)
        assert isinstance(commits_since_tag, int)
        if tag:
            if not re.match(self._version_format_regex, tag, re.IGNORECASE):
                raise VersionParseError("invalid format", tag)

        self.tag = tag
        self.commit_id = commit_id
        self.is_dirty = is_dirty
        self.commits_since_tag = commits_since_tag
        self.components = ""
        self.descriptor = ""
        self._parse_tag()
        self._set_qualified_version()
        self.is_development_build = self.is_dirty or (commits_since_tag > 0)

    def _parse_tag(self):
        match = re.match(self._version_format_regex, self.tag, re.IGNORECASE)
        if match:
            self.components = match.group(1).split(".")
            if match.group(2) is not None:
                self.descriptor = match.group(2)

    def _set_qualified_version(self):
        if self.tag:
            computed_version = self.tag  # use non-empty tag
        else:
            computed_version = "UNTAGGED"  # placeholder to flag user that there are not tags
        if self.commits_since_tag > 0:
            computed_version += ".rev%s+%dcommits" % (self.commit_id, self.commits_since_tag)
        if self.is_dirty:
            computed_version += "-dirty"
        self.qualified_version = computed_version
