import pytest
import os

from version_builder.version_collector import from_file, VersionCollectError
from tests.utils import GitDir


class TestVersionCollectorGit:
    def test_basic(self):
        assert True


class TestVersionCollectorFile:
    def test_valid_file_in_repo(self, tmp_path):
        git_dir = GitDir(tmp_path)
        file = git_dir.path / "version.txt"
        file.write_text("1.2.3-MyDescriptor")
        git_dir.add_all()
        git_dir.commit()
        from_file(file)

    def test_valid_file_outside_repo(self, tmp_path):
        subdir = tmp_path / "my_dir"
        os.mkdir(subdir)
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
