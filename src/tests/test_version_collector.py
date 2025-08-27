from pathlib import Path

import pytest

from tests.utils import GitDir
from version_builder.version_collector import VersionCollectError, from_file, from_git


class TestVersionCollectorGit:
    def test_data_validation(self, tmp_path: Path) -> None:
        git_dir = GitDir(tmp_path)
        git_dir.create_branch("test")
        git_dir.commit()
        git_dir.tag("v1.2.3-alpha.1")  # Collector should strip 'v'
        git_dir.commit()
        expected_commit_id = git_dir.commit()
        version_data = from_git(git_dir.path)
        assert version_data.tag == "1.2.3-alpha.1"  # VersionData gets the stripped tag
        assert expected_commit_id == version_data.commit_id
        assert version_data.commits_since_tag == 2
        assert version_data.branch_name == "test"

    def test_valid_tags(self, tmp_path: Path) -> None:
        git_dir = GitDir(tmp_path)
        git_dir.commit()
        git_dir.tag("1.2.3")
        from_git(git_dir.path)
        git_dir.commit()
        git_dir.tag("1.2.3-alpha-beta")  # Valid SemVer
        from_git(git_dir.path)
        git_dir.commit()
        git_dir.tag("v1.2.3")
        from_git(git_dir.path)
        git_dir.commit()
        git_dir.tag("v1.2.3-rc.1+build.123")  # Valid SemVer with 'v' prefix
        from_git(git_dir.path)

    def test_invalid_tags_are_ignored(self, tmp_path: Path, capsys) -> None:
        git_dir = GitDir(tmp_path)
        git_dir.commit()
        git_dir.tag("1.2.3.4")  # Invalid: too many components
        git_dir.commit()
        git_dir.tag("v1.2.3-Invalid_Tag")  # Invalid: underscore in prerelease
        version_data = from_git(git_dir.path)
        assert version_data.tag == "0.0.0-UNTAGGED"
        assert version_data.commits_since_tag == 2
        captured = capsys.readouterr()
        assert "No valid SemVer tags found in git history. Using '0.0.0-UNTAGGED'." in captured.out

    def test_no_tag(self, tmp_path, capsys):
        git_dir = GitDir(tmp_path)
        git_dir.commit()
        version_data = from_git(git_dir.path)
        assert version_data.tag == "0.0.0-UNTAGGED"
        assert version_data.commits_since_tag == 1
        captured = capsys.readouterr()
        assert "No valid SemVer tags found in git history. Using '0.0.0-UNTAGGED'." in captured.out

    def test_no_repo(self, tmp_path):
        with pytest.raises(VersionCollectError):
            from_git(tmp_path)

    def test_no_commits(self, tmp_path):
        git_dir = GitDir(tmp_path)
        with pytest.raises(VersionCollectError):
            from_git(git_dir.path)

    def test_dirty_repo(self, tmp_path):
        git_dir = GitDir(tmp_path)
        git_dir.commit()
        git_dir.tag("1.2.3")
        file = git_dir.path / "my-file.txt"
        file.write_text("")
        version_data = from_git(git_dir.path)
        assert version_data.is_dirty

    def test_branch_change(self, tmp_path: Path) -> None:
        git_dir = GitDir(tmp_path)
        git_dir.create_branch("test")
        git_dir.commit()
        version_data = from_git(git_dir.path)
        assert version_data.branch_name == "test"
        git_dir.create_branch("new-branch")
        git_dir.commit()
        version_data = from_git(git_dir.path)
        assert version_data.branch_name == "new-branch"

    def test_detached_head(self, tmp_path: Path) -> None:
        git_dir = GitDir(tmp_path)
        detached_commit = git_dir.commit()
        git_dir.commit()
        git_dir.checkout(detached_commit)
        version_data = from_git(git_dir.path)
        assert version_data.branch_name == "HEAD"

    def test_multiple_tags_on_commit(self, tmp_path: Path) -> None:
        git_dir = GitDir(tmp_path)
        git_dir.commit()
        git_dir.tag("v1.0.0")
        git_dir.tag("v1.0.1")
        with pytest.raises(VersionCollectError, match="multiple valid SemVer tags on commit"):
            from_git(git_dir.path)

    def test_mixed_tags_on_commit(self, tmp_path: Path) -> None:
        git_dir = GitDir(tmp_path)
        git_dir.commit()
        git_dir.tag("v1.2.3")
        git_dir.tag("not-semver")
        version_data = from_git(git_dir.path)
        assert version_data.tag == "1.2.3"
        assert version_data.commits_since_tag == 0

    def test_ancestor_semver_tag(self, tmp_path: Path) -> None:
        git_dir = GitDir(tmp_path)
        first_commit = git_dir.commit()
        git_dir.tag("v1.0.0", first_commit)
        git_dir.commit()
        git_dir.tag("not-a-semver-tag")
        git_dir.commit()
        version_data = from_git(git_dir.path)
        assert version_data.tag == "1.0.0"
        assert version_data.commits_since_tag == 2

    def test_multiple_tags_on_ancestor(self, tmp_path: Path) -> None:
        git_dir = GitDir(tmp_path)
        ancestor_commit = git_dir.commit()
        git_dir.tag("v1.0.0", ancestor_commit)
        git_dir.tag("v1.0.1", ancestor_commit)
        git_dir.commit()
        with pytest.raises(VersionCollectError, match="multiple valid SemVer tags on ancestor commit"):
            from_git(git_dir.path)


class TestVersionCollectorFile:
    def test_valid_file_in_repo(self, tmp_path):
        git_dir = GitDir(tmp_path)
        file = git_dir.path / "version.txt"
        file.write_text("v1.2.3-alpha.2")  # File content with 'v'
        git_dir.add_all()
        git_dir.create_branch("test")
        expected_commit_id = git_dir.commit()
        version_data = from_file(file)
        assert expected_commit_id == version_data.commit_id
        assert not version_data.is_dirty
        assert version_data.branch_name == "test"

    def test_valid_file_outside_repo(self, tmp_path: Path) -> None:
        subdir = tmp_path / "my_dir"
        Path.mkdir(subdir)
        git_dir = GitDir(subdir)
        file = tmp_path / "version.txt"
        file.write_text("1.2.3-MyDescriptor")
        git_dir.commit()
        git_dir.commit()
        with pytest.raises(VersionCollectError):
            from_file(file)

    def test_valid_file_no_repo(self, tmp_path: Path) -> None:
        file = tmp_path / "version.txt"
        file.write_text("1.0.0")
        with pytest.raises(VersionCollectError):
            from_file(file)

    def test_empty_file(self, tmp_path: Path) -> None:
        file = tmp_path / "version.txt"
        file.write_text("")
        with pytest.raises(VersionCollectError):
            from_file(file)

    def test_dirty_repo(self, tmp_path: Path) -> None:
        git_dir = GitDir(tmp_path)
        file = git_dir.path / "version.txt"
        file.write_text("1.2.3")
        git_dir.add_all()
        git_dir.commit()
        dirty_file = git_dir.path / "new_file.txt"
        dirty_file.write_text("")
        version_data = from_file(file)
        assert version_data.is_dirty
