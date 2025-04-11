from version_builder.utils import EqualityByValue
import re


class TagInterpretation(EqualityByValue):
    def __init__(self, version_components, version_tag):
        assert isinstance(version_components, list)
        assert all(isinstance(item, str) for item in version_components)
        assert isinstance(version_tag, str)
        self.version_components = version_components
        self.version_tag = version_tag

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class VersionInfo(EqualityByValue):
    def __init__(self, tag_name, commits_since_tag, commit_id, tag_exists, modified_since_commit):
        assert isinstance(tag_name, str)
        assert isinstance(commits_since_tag, int)
        assert isinstance(commit_id, str)
        assert isinstance(tag_exists, bool)
        assert isinstance(modified_since_commit, bool)
        self.tag_name = tag_name
        self.commits_since_tag = commits_since_tag
        self.commit_id = commit_id
        self.tag_exists = tag_exists
        self.modified_since_commit = modified_since_commit
        self.is_dev = modified_since_commit or (not tag_exists) or (commits_since_tag != 0)

    def interpret_tag_name(self):
        matched = re.match(
            r"^v?([0-9]+(?:\.[0-9]+){2})?(?:-([A-Za-z0-9\_/]+))?$",
            self.tag_name,
            re.IGNORECASE,
        )
        if matched:
            version_components = matched.group(1).split(".")
            version_tag = matched.group(2)
            if version_tag is None:
                version_tag = ""
            return TagInterpretation(version_components, version_tag)
        else:
            return None

    @property
    def version_string(self):
        result = ""
        if self.tag_exists:
            result += self.tag_name
        if self.commits_since_tag > 0:
            if result != "":
                result += "."
            result += "dev%d+rev%s" % (self.commits_since_tag, self.commit_id)
        if self.modified_since_commit:
            result += "-modified"
        return result

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)
