import pytest

from version_builder.version_data import VersionData, VersionParseError


class TestVersionDataSemVerParsing:
    def test_no_tag_not_allowed(self):
        with pytest.raises(VersionParseError):
            VersionData(tag="", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)

    def test_tag_not_dirty_default_commits(self):
        data = VersionData(tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=False)
        assert data.qualified_version == "1.2.3+abcd1234"
        assert data.major == 1
        assert data.minor == 2
        assert data.patch == 3
        assert data.prerelease == ""
        assert data.buildmetadata_from_tag == ""
        assert data.full_build_metadata == "abcd1234"

    def test_tag_dirty_default_commits(self):
        data = VersionData(tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=True)
        assert data.qualified_version == "1.2.3+abcd1234.dirty"
        assert data.full_build_metadata == "abcd1234.dirty"

    def test_tag_not_dirty_new_commits(self):
        data = VersionData(
            tag="1.2.3", commit_id="abcd1234", branch_name="myBranch", is_dirty=False, commits_since_tag=5
        )
        assert data.qualified_version == "1.2.3+dev.5.abcd1234"
        assert data.full_build_metadata == "dev.5.abcd1234"

    def test_full_semver_tag_data_verification(self):
        input_tag = "1.0.0-alpha.1+build.original"
        expected_commit_id = "abcd1234"
        expected_branch_name = "test/branch"
        expected_is_dirty = True
        expected_commits_since_tag = 5
        expected_major = 1
        expected_minor = 0
        expected_patch = 0
        expected_prerelease = "alpha.1"
        expected_buildmetadata_from_tag = "build.original"
        expected_is_development_build = True
        expected_full_build_metadata = "build.original.dev.5.abcd1234.dirty"
        expected_qualified_version = f"1.0.0-alpha.1+{expected_full_build_metadata}"

        data = VersionData(
            tag=input_tag,
            commit_id=expected_commit_id,
            branch_name=expected_branch_name,
            is_dirty=expected_is_dirty,
            commits_since_tag=expected_commits_since_tag,
        )
        assert expected_qualified_version == data.qualified_version
        assert input_tag == data.tag  # raw input tag
        assert expected_commit_id == data.commit_id
        assert expected_branch_name == data.branch_name
        assert expected_is_dirty == data.is_dirty
        assert [expected_major, expected_minor, expected_patch] == data.components
        assert expected_prerelease == data.prerelease
        assert expected_buildmetadata_from_tag == data.buildmetadata_from_tag
        assert expected_full_build_metadata == data.full_build_metadata
        assert expected_is_development_build == data.is_development_build

    def test_tag_with_prerelease_only(self):
        data = VersionData(tag="2.0.1-beta.2", commit_id="abcd1234", branch_name="b")
        assert data.major == 2
        assert data.minor == 0
        assert data.patch == 1
        assert data.prerelease == "beta.2"
        assert data.buildmetadata_from_tag == ""
        assert data.qualified_version == "2.0.1-beta.2+abcd1234"
        assert data.full_build_metadata == "abcd1234"

    def test_tag_with_build_metadata_only(self):
        data = VersionData(tag="0.0.1+exp.sha.5114f85", commit_id="abcd1234", branch_name="b", is_dirty=True)
        assert data.major == 0
        assert data.minor == 0
        assert data.patch == 1
        assert data.prerelease == ""
        assert data.buildmetadata_from_tag == "exp.sha.5114f85"
        assert data.qualified_version == "0.0.1+exp.sha.5114f85.abcd1234.dirty"
        assert data.full_build_metadata == "exp.sha.5114f85.abcd1234.dirty"

    def test_invalid_semver_tags(self):
        invalid_tags = [
            "v1.2.3",  # 'v' prefix is handled by collector, not VersionData directly
            "a1.2.3",  # Invalid char at start
            "1.2",  # Missing patch component
            "1.2.3.4",  # Too many components
            "1.2.3-alpha_beta",  # Underscore in prerelease identifier
            "1.2.3-alpha..beta",  # Empty prerelease identifier
            "1.2.3-01",  # Leading zero in numeric prerelease identifier
            "1.2.3-alpha!",  # Invalid char in prerelease
            "1.2.3+build_meta",  # Underscore in build metadata (SemVer allows only [0-9A-Za-z-])
            "1.2.3+build..meta",  # Empty build metadata identifier
            "1.2.3+",  # Empty build metadata
            "1.2.3-",  # Empty prerelease
            "Invalid-TAG",
            "1.2.3 MyDescriptor",
            "1.2.3MyDescriptor",
        ]
        for invalid_tag in invalid_tags:
            with pytest.raises(VersionParseError, match="invalid SemVer 2.0.0 format"):
                VersionData(tag=invalid_tag, commit_id="id", branch_name="b")


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
