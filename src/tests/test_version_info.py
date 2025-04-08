from version_builder.version_info import VersionInfo, TagInterpretation


class TestVersionInfo:
    def test_equals(self):
        assert VersionInfo("v1.6.0", 20, "23fa", True, False) == VersionInfo("v1.6.0", 20, "23fa", True, False)

    def test_not_equals_tag(self):
        assert VersionInfo("v1.6.0", 20, "23fa", True, False) != VersionInfo("v1.6.1", 20, "23fa", True, False)

    def test_not_equals_commits_since_tag(self):
        assert VersionInfo("v1.6.1", 20, "23fa", True, False) != VersionInfo("v1.6.1", 21, "23fa", True, False)

    def test_not_equals_commit_id(self):
        assert VersionInfo("v1.6.1", 20, "23fa", True, False) != VersionInfo("v1.6.1", 20, "23fb", True, False)

    def test_not_equals_is_tag(self):
        assert VersionInfo("v1.6.1", 20, "23fa", True, False) != VersionInfo("v1.6.1", 20, "23fa", False, False)

    def test_not_equals_modified_since_commit(self):
        assert VersionInfo("v1.6.1", 20, "23fa", True, False) != VersionInfo("v1.6.1", 20, "23fa", True, True)

    def test_version_string_for_tag(self):
        assert "v1.5" == VersionInfo("v1.5", 0, "23fa", True, False).version_string

    def test_version_string_for_tag_no_prefix(self):
        assert "1.5" == VersionInfo("1.5", 0, "23fa", True, False).version_string

    def test_version_string_for_tag_modified(self):
        assert "v1.5-modified" == VersionInfo("v1.5", 0, "23fa", True, True).version_string

    def test_version_string_with_no_tag(self):
        assert "dev2+rev23fa" == VersionInfo("develop", 2, "23fa", False, False).version_string

    def test_version_string_with_no_tag_modified(self):
        assert "dev2+rev23fa-modified" == VersionInfo("develop", 2, "23fa", False, True).version_string

    def test_version_string_with_commits_since_tag(self):
        assert "v1.5.dev2+rev23fa" == VersionInfo("v1.5", 2, "23fa", True, False).version_string

    def test_version_string_with_commits_since_tag_modified(self):
        assert "v1.5.dev2+rev23fa-modified" == VersionInfo("v1.5", 2, "23fa", True, True).version_string

    def test_is_dev_commit_since_tag(self):
        assert VersionInfo("1.0", 3, "23fa", True, False).is_dev

    def test_is_dev_no_tag(self):
        assert VersionInfo("1.0", 0, "23fa", False, False).is_dev

    def test_is_dev_modified(self):
        assert VersionInfo("1.0", 0, "23fa", True, True).is_dev

    def test_is_not_dev(self):
        assert not VersionInfo("1.0", 0, "23fa", True, False).is_dev

    def test_interpret_valid_tag_name(self):
        assert (
            TagInterpretation(["1", "2", "3"], "") == VersionInfo("1.2.3", 0, "23fa", True, False).interpret_tag_name()
        )

    def test_interpret_valid_tag_name_human_string(self):
        assert (
            TagInterpretation(["1", "0", "3"], "MyMilestone_RC3")
            == VersionInfo("1.0.3-MyMilestone_RC3", 0, "23fa", True, False).interpret_tag_name()
        )

    def test_interpret_invalid_tag_name_human_no_separator(self):
        assert None is VersionInfo("1.0.3MyMilestone_RC3", 0, "23fa", True, False).interpret_tag_name()

    def test_interpret_invalid_tag_name_human_contains_dash(self):
        assert None is VersionInfo("1.0.3-MyMilestone-RC3", 0, "23fa", True, False).interpret_tag_name()

    def test_interpret_invalid_tag_name_human_contains_period(self):
        assert None is VersionInfo("1.2.3-MyMilestone.RC3", 0, "23fa", True, False).interpret_tag_name()

    def test_interpret_valid_tag_name_with_zeroes_in_component(self):
        assert (
            TagInterpretation(["1", "020", "3"], "beta")
            == VersionInfo("1.020.3-beta", 0, "23fa", True, False).interpret_tag_name()
        )

    def test_interpret_valid_tag_name_of_dev_version_1(self):
        assert (
            TagInterpretation(["0", "8", "1"], "") == VersionInfo("0.8.1", 1, "23fa", True, False).interpret_tag_name()
        )

    def test_interpret_valid_tag_name_of_dev_version_2(self):
        assert (
            TagInterpretation(["0", "8", "1"], "MyMilestone_RC3")
            == VersionInfo("0.8.1-MyMilestone_RC3", 123, "23fa", True, False).interpret_tag_name()
        )

    def test_interpret_invalid_tag_name(self):
        assert None is VersionInfo("develop", 0, "23fa", True, False).interpret_tag_name()

    def test_interpret_invalid_tag_name_invalid_number(self):
        assert None is VersionInfo("develop-alpha", 0, "23fa", True, False).interpret_tag_name()

    def test_interpret_invalid_tag_name_invalid_component_separator(self):
        assert None is VersionInfo("1,0-alpha", 0, "23fa", True, False).interpret_tag_name()

    def test_interpret_invalid_tag_name_invalid_missing_component(self):
        assert None is VersionInfo("1..3", 0, "23fa", True, False).interpret_tag_name()

    def test_interpret_invalid_tag_name_invalid_human_separator(self):
        assert None is VersionInfo("1.2.-alpha", 0, "23fa", True, False).interpret_tag_name()

    def test_interpret_invalid_component_number(self):
        assert None is VersionInfo("1.2", 0, "23fa", True, False).interpret_tag_name()


# These tests form the base of TestVersionInfo
class TestTagInterpretation:
    def test_equals(self):
        assert TagInterpretation(["1", "2", "3"], "MyMilestone_RC3") == TagInterpretation(
            ["1", "2", "3"], "MyMilestone_RC3"
        )

    def test_not_equals_version_tag(self):
        assert TagInterpretation(["1", "2", "3"], "MyMilestone_RC3") != TagInterpretation(
            ["1", "2", "3"], "MyMilestone"
        )

    def test_not_equals_component_length(self):
        assert TagInterpretation(["1", "2", "3"], "MyMilestone_RC3") != TagInterpretation(["1", "2"], "MyMilestone_RC3")

    def test_not_equals_components_value(self):
        assert TagInterpretation(["1", "2", "3"], "MyMilestone_RC3") != TagInterpretation(
            ["1", "2", "4"], "MyMilestone_RC3"
        )
