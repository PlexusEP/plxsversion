from pathlib import Path

from tests.utils import GitDir
from version_builder import utils


class TestDirectoryManagement:
    def test_change_dir(self):
        current_dir = Path.cwd()
        with utils.change_dir("/"):
            assert Path.cwd() == Path("/")
        assert Path.cwd() == current_dir


class TestGitWrapper:
    def test_commit_count_no_commits(self, tmp_path):
        git_dir = GitDir(tmp_path)
        with utils.change_dir(git_dir.path):
            assert utils.Git.get_commit_count() == 0

    def test_commit_count(self, tmp_path):
        git_dir = GitDir(tmp_path)
        with utils.change_dir(git_dir.path):
            for commit_num in range(1, 5):
                git_dir.commit()
                assert commit_num == utils.Git.get_commit_count()

    def test_get_commit_id(self, tmp_path: Path) -> None:
        git_dir = GitDir(tmp_path)
        with utils.change_dir(git_dir.path):
            short_id_from_helper = git_dir.commit()

            # Test default (short=True)
            short_id_from_util = utils.Git.get_commit_id()
            assert short_id_from_util == short_id_from_helper
            assert len(short_id_from_util) == 7

            # Test short=False
            full_id_from_util = utils.Git.get_commit_id(short=False)
            assert len(full_id_from_util) == 40
            assert full_id_from_util.startswith(short_id_from_util)

            # Test short=True explicitly
            assert utils.Git.get_commit_id(short=True) == short_id_from_util

    def test_cwd_not_empty(self, tmp_path):
        git_dir = GitDir(tmp_path)
        with utils.change_dir(git_dir.path):
            assert not utils.Git.get_cwd_is_not_empty()
            file = git_dir.path / "my-file.txt"
            file.write_text("")
            assert utils.Git.get_cwd_is_not_empty()

    def test_dirty_detection(self, tmp_path):
        git_dir = GitDir(tmp_path)
        with utils.change_dir(git_dir.path):
            git_dir.commit()
            assert not utils.Git.get_is_dirty()  # empty repo
            file = git_dir.path / "my-file.txt"
            file.write_text("")
            assert utils.Git.get_is_dirty()  # untracked change
            git_dir.add_all()
            assert utils.Git.get_is_dirty()  # staged change
            git_dir.commit()
            assert not utils.Git.get_is_dirty()  # no changes
            file.write_text("hello")
            assert utils.Git.get_is_dirty()  # unstaged changes
