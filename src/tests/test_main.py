import subprocess
import sys
import os
from tests.utils import GitDir, TempDir
from version_builder import main
from version_builder.getter import VersionInfo


# These tests ensure the public functions in main create the desired results
# More stringent validation is done in other tests
class TestPublicInterface:
    def test_get_version_from_git(self):
        tag = "v1.2.3-test"
        with GitDir() as git:
            commit_id = git.create_git_commit()
            git.create_git_tag(tag)
            expected = VersionInfo(tag, 0, commit_id, True, False)
            result = main.get_version_from_git(git.path)
            assert expected == result

    def test_create_file_from_git_expect_file_with_content(self):
        with GitDir() as git, TempDir() as out_dir:
            git.create_git_commit()
            main.create_version_file_from_git(git.path, out_dir, "cpp")
            out_file = out_dir + "/version.hpp"
            assert os.path.exists(out_file)


# These tests ensure the correct version file is created with content for a given lang
# Tests for language specific formatting is done elsewhere
class TestLanguages:
    def test_cpp(self):
        with GitDir() as git, TempDir() as out_dir:
            git.create_git_commit()
            main.create_version_file_from_git(git.path, out_dir, "cpp")
            out_file = out_dir + "/version.hpp"
            assert os.path.exists(out_file)
            assert os.stat(out_file).st_size != 0


# These tests ensure invoking this as a module is successful
class TestMainIntegration:
    def test_output_created_with_content(self):
        with GitDir() as git, TempDir() as out_dir:
            git.create_git_commit()
            script_dir = os.getcwd() + "/src"
            with open("/dev/null", "w") as devnull:
                subprocess.check_call(
                    [sys.executable, "-m", "version_builder", "--lang", "cpp", "--gitdir", git.path, out_dir],
                    stdout=devnull,
                    env={"PYTHONPATH": script_dir},
                )
            out_file = out_dir + "/version.hpp"
            assert os.path.exists(out_file)
            assert os.stat(out_file).st_size != 0
