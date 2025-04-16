import os
from version_builder import utils


class TestUtils:
    def test_change_dir(self):
        current_dir = os.getcwd()
        with utils.change_dir("/"):
            assert os.getcwd() == "/"
        assert os.getcwd() == current_dir
