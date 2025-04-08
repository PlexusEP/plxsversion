import pytest

from version_builder import getter
from version_builder.version_info import VersionInfo
from tests.utils import GitDir


class TestParseGitVersion:
    def test_parse_git_version_simple(self):
        obj = getter._parse_git_version("v1.6.2-0-g3f2a", False)
        assert VersionInfo("v1.6.2", 0, "3f2a", True, False) == obj

    def test_parse_git_version_simple_no_prefix(self):
        obj = getter._parse_git_version("1.6.2-0-g3f2a", False)
        assert VersionInfo("1.6.2", 0, "3f2a", True, False) == obj

    def test_parse_git_version_with_commits_since_tag(self):
        obj = getter._parse_git_version("v1.6.3-23-g49302", False)
        assert VersionInfo("v1.6.3", 23, "49302", True, False) == obj

    def test_parse_git_version_with_human_field(self):
        obj = getter._parse_git_version("v1.6.3-MyMilestone-20-gfade", False)
        assert VersionInfo("v1.6.3-MyMilestone", 20, "fade", True, False) == obj

    def test_parse_git_version_human_field_underscore(self):
        obj = getter._parse_git_version("v1.6.3-MyMilestone_RC3-0-gfade", False)
        assert VersionInfo("v1.6.3-MyMilestone_RC3", 0, "fade", True, False) == obj

    def test_parse_git_version_with_slashes_in_tag(self):
        obj = getter._parse_git_version("/heads/develop-20-gfade", False)
        assert VersionInfo("/heads/develop", 20, "fade", True, False) == obj

    def test_parse_git_version_missing_tag(self):
        with pytest.raises(getter.VersionParseError):
            getter._parse_git_version("23-gfade", False)

    def test_parse_git_version_empty_tag(self):
        with pytest.raises(getter.VersionParseError):
            getter._parse_git_version("-23-gfade", False)

    def test_parse_git_version_missing_commits_since_tag(self):
        with pytest.raises(getter.VersionParseError):
            getter._parse_git_version("v2.3-gfade", False)

    def test_parse_git_version_empty_commits_since_tag(self):
        with pytest.raises(getter.VersionParseError):
            getter._parse_git_version("v2.3--gfade", False)

    def test_parse_git_version_commits_since_tag_not_int(self):
        with pytest.raises(getter.VersionParseError):
            getter._parse_git_version("v2.3-a2-gfade", False)

    def test_parse_git_version_missing_commit_id(self):
        with pytest.raises(getter.VersionParseError):
            getter._parse_git_version("v2.3-20", False)

    def test_parse_git_version_empty_commit_id(self):
        with pytest.raises(getter.VersionParseError):
            getter._parse_git_version("v2.3-20-", False)


class TestFromGit:
    def test_empty(self):
        with GitDir() as directory:
            version_info = getter.from_git(directory.path)
            assert VersionInfo("HEAD", 0, "0", False, False) == version_info

    def test_commit_no_tag(self):
        with GitDir() as directory:
            commit_id = directory.create_git_commit()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("main", 1, commit_id, False, False) == version_info

    def test_multiple_commits_no_tag(self):
        with GitDir() as directory:
            directory.create_git_commit()
            directory.create_git_commit()
            commit_id = directory.create_git_commit()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("main", 3, commit_id, False, False) == version_info

    def test_commit_tag(self):
        with GitDir() as directory:
            commit_id = directory.create_git_commit()
            directory.create_git_tag("tagname")
            version_info = getter.from_git(directory.path)
            assert VersionInfo("tagname", 0, commit_id, True, False) == version_info

    def test_commit_tag_commit(self):
        with GitDir() as directory:
            directory.create_git_commit()
            directory.create_git_tag("tagname")
            commit_id = directory.create_git_commit()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("tagname", 1, commit_id, True, False) == version_info

    def test_commit_tag_multiple_commits(self):
        with GitDir() as directory:
            directory.create_git_commit()
            directory.create_git_tag("tagname")
            directory.create_git_commit()
            commit_id = directory.create_git_commit()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("tagname", 2, commit_id, True, False) == version_info

    def test_commit_tag_commit_tag_commit(self):
        with GitDir() as directory:
            directory.create_git_commit()
            directory.create_git_tag("tagname")
            directory.create_git_commit()
            directory.create_git_tag("mytag2")
            commit_id = directory.create_git_commit()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("mytag2", 1, commit_id, True, False) == version_info

    def test_commit_commit_tag_rewind(self):
        with GitDir() as directory:
            directory.create_git_commit()
            commit_id = directory.create_git_commit()
            directory.create_git_commit()
            directory.create_git_tag("tagname")
            directory.checkout_git_commit(commit_id)
            version_info = getter.from_git(directory.path)
            assert VersionInfo("HEAD", 2, commit_id, False, False) == version_info

    def test_commit_tag_commit_commit_tag_rewind(self):
        with GitDir() as directory:
            directory.create_git_commit()
            directory.create_git_tag("tagname")
            commit_id = directory.create_git_commit()
            directory.create_git_commit()
            directory.create_git_tag("mytag2")
            directory.checkout_git_commit(commit_id)
            version_info = getter.from_git(directory.path)
            assert VersionInfo("tagname", 1, commit_id, True, False) == version_info

    def test_commit_branch(self):
        with GitDir() as directory:
            commit_id = directory.create_git_commit()
            directory.create_git_branch("newbranch")
            version_info = getter.from_git(directory.path)
            assert VersionInfo("newbranch", 1, commit_id, False, False) == version_info

    def test_commit_branch_commit(self):
        with GitDir() as directory:
            directory.create_git_commit()
            directory.create_git_branch("newbranch")
            commit_id = directory.create_git_commit()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("newbranch", 2, commit_id, False, False) == version_info

    def test_commit_tag_commit_branch_commit(self):
        with GitDir() as directory:
            directory.create_git_commit()
            directory.create_git_tag("mytag")
            directory.create_git_commit()
            directory.create_git_branch("newbranch")
            commit_id = directory.create_git_commit()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("mytag", 2, commit_id, True, False) == version_info

    def test_commit_branchedcommit(self):
        with GitDir() as directory:
            commit_id = directory.create_git_commit()
            directory.create_git_branch("newbranch")
            directory.create_git_commit()
            directory.switch_git_branch("main")
            version_info = getter.from_git(directory.path)
            assert VersionInfo("main", 1, commit_id, False, False) == version_info

    def test_commit_branchedtaggedcommit(self):
        with GitDir() as directory:
            commit_id = directory.create_git_commit()
            directory.create_git_branch("newbranch")
            directory.create_git_commit()
            directory.create_git_tag("mytag")
            directory.switch_git_branch("main")
            version_info = getter.from_git(directory.path)
            assert VersionInfo("main", 1, commit_id, False, False) == version_info

    def test_commit_tag_branchedtaggedcommit(self):
        with GitDir() as directory:
            commit_id = directory.create_git_commit()
            directory.create_git_tag("originaltag")
            directory.create_git_branch("newbranch")
            directory.create_git_commit()
            directory.create_git_tag("newtag")
            directory.switch_git_branch("main")
            version_info = getter.from_git(directory.path)
            assert VersionInfo("originaltag", 0, commit_id, True, False) == version_info

    def test_commit_tag_commit_branchedtaggedcommit(self):
        with GitDir() as directory:
            directory.create_git_commit()
            directory.create_git_tag("originaltag")
            commit_id = directory.create_git_commit()
            directory.create_git_branch("newbranch")
            directory.create_git_commit()
            directory.create_git_tag("newtag")
            directory.switch_git_branch("main")
            version_info = getter.from_git(directory.path)
            assert VersionInfo("originaltag", 1, commit_id, True, False) == version_info

    # -------------------------------------------------------------
    # Test that local uncommitted changes are recognized correctly
    # -------------------------------------------------------------

    def test_empty_with_untracked_file(self):
        with GitDir() as directory:
            directory.add_untracked_file()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("HEAD", 0, "0", False, True) == version_info

    def test_empty_with_tracked_file(self):
        with GitDir() as directory:
            directory.add_tracked_file()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("HEAD", 0, "0", False, True) == version_info

    def test_commit_with_untracked_file(self):
        with GitDir() as directory:
            commit_id = directory.create_git_commit()
            directory.add_untracked_file()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("main", 1, commit_id, False, True) == version_info

    def test_commit_with_tracked_file(self):
        with GitDir() as directory:
            commit_id = directory.create_git_commit()
            directory.add_tracked_file()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("main", 1, commit_id, False, True) == version_info

    def test_commit_with_modified_file(self):
        with GitDir() as directory:
            filename = directory.add_tracked_file()
            commit_id = directory.create_git_commit()
            directory.modify_file(filename)
            version_info = getter.from_git(directory.path)
            assert VersionInfo("main", 1, commit_id, False, True) == version_info

    def test_tag_with_untracked_file(self):
        with GitDir() as directory:
            commit_id = directory.create_git_commit()
            directory.create_git_tag("mytag")
            directory.add_untracked_file()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("mytag", 0, commit_id, True, True) == version_info

    def test_tag_with_tracked_file(self):
        with GitDir() as directory:
            commit_id = directory.create_git_commit()
            directory.create_git_tag("mytag")
            directory.add_tracked_file()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("mytag", 0, commit_id, True, True) == version_info

    def test_tag_with_modified_file(self):
        with GitDir() as directory:
            filename = directory.add_tracked_file()
            commit_id = directory.create_git_commit()
            directory.create_git_tag("mytag")
            directory.modify_file(filename)
            version_info = getter.from_git(directory.path)
            assert VersionInfo("mytag", 0, commit_id, True, True) == version_info

    def test_tag_commit_with_untracked_file(self):
        with GitDir() as directory:
            directory.create_git_commit()
            directory.create_git_tag("mytag")
            commit_id = directory.create_git_commit()
            directory.add_untracked_file()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("mytag", 1, commit_id, True, True) == version_info

    def test_tag_commit_with_tracked_file(self):
        with GitDir() as directory:
            directory.create_git_commit()
            directory.create_git_tag("mytag")
            commit_id = directory.create_git_commit()
            directory.add_tracked_file()
            version_info = getter.from_git(directory.path)
            assert VersionInfo("mytag", 1, commit_id, True, True) == version_info

    def test_tag_commit_with_modified_file(self):
        with GitDir() as directory:
            filename = directory.add_tracked_file()
            directory.create_git_commit()
            directory.create_git_tag("mytag")
            commit_id = directory.create_git_commit()
            directory.modify_file(filename)
            version_info = getter.from_git(directory.path)
            assert VersionInfo("mytag", 1, commit_id, True, True) == version_info
