
from generalpackager.api.pypi import PyPI
from generalfile.test.setup_workdir import setup_workdir
from generallibrary import Date

import unittest


class TestPyPI(unittest.TestCase):
    def test_exists(self):
        self.assertEqual(True, PyPI("generalpackager").exists())
        self.assertEqual(False, PyPI("random-package_that,cant.exist").exists())

    def test_get_tarball_url(self):
        pypi = PyPI("generalpackager")
        self.assertEqual(True, pypi.name in pypi.get_tarball_url())
        self.assertEqual(True, pypi.name in pypi.get_tarball_url(version="1.0.0"))

    def test_download(self):
        setup_workdir(use_working_dir=True)

        path = PyPI("generalpackager").download(path="repo")
        self.assertEqual(True, "generalpackager" in path.get_child())

        with self.assertRaises(AttributeError):
            PyPI("generalpackager").download(path="repo", version="0.0.111")

        path = PyPI("generalpackager").download(path="repo", version="0.0.11", overwrite=True)
        self.assertEqual(2, len(path.get_parent().get_children()))

    def test_get_owners_packages(self):
        github = PyPI()
        self.assertEqual(set(), {"generallibrary", "generalfile", "generalvector", "generalpackager"}.difference(github.get_owners_packages()))

    def test_get_version(self):
        self.assertEqual(True, PyPI("generalpackager").get_version() > "0.2.0")

    def test_get_date(self):
        self.assertLess(PyPI("generalpackager").get_date(), Date.now())

    def test_reserve_name(self):
        pass























