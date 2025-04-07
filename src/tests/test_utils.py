import os
from version_builder import utils


class TestUtils:
    def test_chdir(self):
        curdir = os.getcwd()
        with utils.ChDir("/"):
            assert os.getcwd() == "/"
        assert os.getcwd() == curdir
