import pytest

from version_builder.version_data import VersionData, VersionParseError


class TestVersionDataTag:
    def test_no_tag_not_allowed(self):
        with pytest.raises(VersionParseError):
            VersionData(tag="", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)

    # Semantic version testing
    def test_tag_not_dirty_default_commits(self):
        expected_qualified_version = "1.2.3"
        data = VersionData(tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        assert expected_qualified_version == data.qualified_version

    def test_tag_dirty_default_commits(self):
        expected_qualified_version = "1.2.3-dirty"
        data = VersionData(tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=True)
        assert expected_qualified_version == data.qualified_version

    def test_tag_not_dirty_new_commits(self):
        expected_qualified_version = "1.2.3.revabcd1234+5commits"
        data = VersionData(
            tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=False, commits_since_tag=5
        )
        assert expected_qualified_version == data.qualified_version

    # (alternative name) test_tag_dirty_new_commits
    def test_tag_data_verification(self):
        expected_tag = "1.2.3"
        expected_commit_id = "abcd1234"
        expected_branch_name = "test/branch"
        expected_is_dirty = True
        expected_components = [1, 2, 3]
        expected_descriptor = ""
        expected_is_development_build = True
        expected_qualified_version = "1.2.3.revabcd1234+5commits-dirty"
        data = VersionData(
            tag="1.2.3", commit_id="abcd1234", branch_name="test/branch", is_dirty=True, commits_since_tag=5
        )
        assert expected_qualified_version == data.qualified_version
        assert expected_tag == data.tag
        assert expected_commit_id == data.commit_id
        assert expected_branch_name == data.branch_name
        assert expected_is_dirty == data.is_dirty
        assert expected_components == data.components
        assert expected_descriptor == data.descriptor
        assert expected_is_development_build == data.is_development_build

    def test_tag_leading_char(self):
        expected_tag = "v1.2.3"
        expected_components = [1, 2, 3]
        expected_qualified_version = "v1.2.3"
        data = VersionData(tag="v1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        assert expected_qualified_version == data.qualified_version
        assert expected_tag == data.tag
        assert expected_components == data.components

    def test_tag_bad_leading_char(self):
        with pytest.raises(VersionParseError):
            VersionData(tag="a1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)

    def test_tag_enforce_semantic_versioning(self):
        with pytest.raises(VersionParseError):
            # missing field
            VersionData(tag="1.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        with pytest.raises(VersionParseError):
            # extra field
            VersionData(tag="1.2.3.4", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)

    def test_tag_is_all_text(self):
        with pytest.raises(VersionParseError):
            VersionData(tag="Invalid-TAG", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        with pytest.raises(VersionParseError):
            VersionData(tag="InvalidTAG", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        with pytest.raises(VersionParseError):
            VersionData(tag="Invalid TAG", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        with pytest.raises(VersionParseError):
            VersionData(tag="Invalid_TAG", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)


class TestVersionDataDescriptor:
    def test_valid_formats(self):
        VersionData(
            tag="1.2.3-MyDescriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=True, commits_since_tag=5
        )
        VersionData(
            tag="1.2.3-MyDescriptor1", commit_id="abcd1234", branch_name="myBranch", is_dirty=True, commits_since_tag=5
        )
        VersionData(
            tag="1.2.3-My_Descriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=True, commits_since_tag=5
        )
        VersionData(
            tag="1.2.3-1My_Descriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=True, commits_since_tag=5
        )

    def test_data_verification(self):
        expected_components = [1, 2, 3]
        expected_descriptor = "1My_Descriptor2"
        expected_qualified_version = "1.2.3-1My_Descriptor2.revabcd1234+5commits-dirty"
        data = VersionData(
            tag="1.2.3-1My_Descriptor2",
            commit_id="abcd1234",
            branch_name="myBranch",
            is_dirty=True,
            commits_since_tag=5,
        )
        assert expected_qualified_version == data.qualified_version
        assert expected_components == data.components
        assert expected_descriptor == data.descriptor

    def test_invalid_content(self):
        with pytest.raises(VersionParseError):
            VersionData(tag="1.2.3-My-Descriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        with pytest.raises(VersionParseError):
            VersionData(tag="1.2.3-My.Descriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        with pytest.raises(VersionParseError):
            VersionData(tag="1.2.3-MyDescriptor!", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)

    def test_invalid_separator(self):
        with pytest.raises(VersionParseError):
            VersionData(tag="1.2.3MyDescriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        with pytest.raises(VersionParseError):
            VersionData(tag="1.2.3 MyDescriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        with pytest.raises(VersionParseError):
            VersionData(tag="1.2.3_MyDescriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        with pytest.raises(VersionParseError):
            VersionData(tag="1.2.3/MyDescriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)

    def test_invalid_semantic_version(self):
        with pytest.raises(VersionParseError):
            VersionData(tag="-MyDescriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        with pytest.raises(VersionParseError):
            VersionData(tag="1.3-MyDescriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        with pytest.raises(VersionParseError):
            VersionData(tag="1.2.3.4-MyDescriptor", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)


class TestVersionDataDevelopmentFlag:
    def test_not_dirty_no_commits(self):
        data = VersionData(
            tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=False, commits_since_tag=0
        )
        assert not data.is_development_build

    def test_dirty_no_commits(self):
        data = VersionData(
            tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=True, commits_since_tag=0
        )
        assert data.is_development_build

    def test_not_dirty_new_commits(self):
        data = VersionData(
            tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=False, commits_since_tag=1
        )
        assert data.is_development_build

    def test_dirty_new_commits(self):
        data = VersionData(
            tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=True, commits_since_tag=1
        )
        assert data.is_development_build


class TestVersionDataTime:
    def test_never_set(self):
        data = VersionData(
            tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=False, commits_since_tag=0
        )
        assert data.time == ""

    def test_set_called(self):
        data = VersionData(
            tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=False, commits_since_tag=0
        )
        data.set_time()
        assert data.time != ""
