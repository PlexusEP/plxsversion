from pathlib import Path

import pytest

from tests.utils import GitDir
from version_builder.version_collector import VersionCollectError, from_file, from_git
from version_builder.version_data import VersionParseError


class TestVersionCollectorGit:
    def test_data_validation(self, tmp_path):
        git_dir = GitDir(tmp_path)
        git_dir.create_branch("test")
        git_dir.commit()
        git_dir.tag("v1.2.3-My_Descriptor_123")
        git_dir.commit()
        expected_commit_id = git_dir.commit()
        version_data = from_git(git_dir.path)
        assert version_data.tag == "v1.2.3-My_Descriptor_123"
        assert expected_commit_id == version_data.commit_id
        assert version_data.commits_since_tag == 2
        assert version_data.branch_name == "test"

    def test_valid_tags(self, tmp_path):
        git_dir = GitDir(tmp_path)
        git_dir.commit()
        git_dir.tag("1.2.3")
        from_git(git_dir.path)
        git_dir.commit()
        git_dir.tag("1.2.3-My_Descriptor_123")
        from_git(git_dir.path)
        git_dir.commit()
        git_dir.tag("v1.2.3")
        from_git(git_dir.path)
        git_dir.commit()
        git_dir.tag("v1.2.3-My_Descriptor_123")
        from_git(git_dir.path)

    def test_invalid_tag(self, tmp_path):
        git_dir = GitDir(tmp_path)
        git_dir.commit()
        git_dir.tag("1.2.3.4")
        with pytest.raises(VersionParseError):
            from_git(git_dir.path)

    def test_no_tag(self, tmp_path):
        git_dir = GitDir(tmp_path)
        git_dir.commit()
        version_data = from_git(git_dir.path)
        assert version_data.tag == "0.0.0-UNTAGGED"

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

    def test_branch_change(self, tmp_path):
        git_dir = GitDir(tmp_path)
        git_dir.create_branch("test")
        git_dir.commit()
        version_data = from_git(git_dir.path)
        assert version_data.branch_name == "test"
        git_dir.create_branch("new-branch")
        git_dir.commit()
        version_data = from_git(git_dir.path)
        assert version_data.branch_name == "new-branch"

    def test_detached_head(self, tmp_path):
        git_dir = GitDir(tmp_path)
        detached_commit = git_dir.commit()
        git_dir.commit()
        git_dir.checkout(detached_commit)
        version_data = from_git(git_dir.path)
        assert version_data.branch_name == "HEAD"


class TestVersionCollectorFile:
    def test_valid_file_in_repo(self, tmp_path):
        git_dir = GitDir(tmp_path)
        file = git_dir.path / "version.txt"
        file.write_text("1.2.3-MyDescriptor")
        git_dir.add_all()
        git_dir.create_branch("test")
        expected_commit_id = git_dir.commit()
        version_data = from_file(file)
        assert expected_commit_id == version_data.commit_id
        assert not version_data.is_dirty
        assert version_data.branch_name == "test"

    def test_valid_file_outside_repo(self, tmp_path):
        subdir = tmp_path / "my_dir"
        Path.mkdir(subdir)
        git_dir = GitDir(subdir)
        file = tmp_path / "version.txt"
        file.write_text("1.2.3-MyDescriptor")
        git_dir.commit()
        git_dir.commit()
        with pytest.raises(VersionCollectError):
            from_file(file)

    def test_valid_file_no_repo(self, tmp_path):
        file = tmp_path / "version.txt"
        file.write_text("1.2.3-MyDescriptor")
        with pytest.raises(VersionCollectError):
            from_file(file)

    def test_empty_file(self, tmp_path):
        file = tmp_path / "version.txt"
        file.write_text("")
        with pytest.raises(VersionCollectError):
            from_file(file)

    def test_dirty_repo(self, tmp_path):
        git_dir = GitDir(tmp_path)
        file = git_dir.path / "version.txt"
        file.write_text("1.2.3-MyDescriptor")
        git_dir.add_all()
        git_dir.commit()
        dirty_file = git_dir.path / "new_file.txt"
        dirty_file.write_text("")
        version_data = from_file(file)
        assert version_data.is_dirty
