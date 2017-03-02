import unittest

from flake8.main import application


class TestCodeStyle(unittest.TestCase):

    def test_run_flake8(self):
        flake8 = application.Application('..')
        flake8.run(['--max-line-length', '159', '--exclude', 'private'])
        failed = (flake8.result_count > 0) or flake8.catastrophic_failure
        self.assertFalse(failed, "flake8 code style check failed")
