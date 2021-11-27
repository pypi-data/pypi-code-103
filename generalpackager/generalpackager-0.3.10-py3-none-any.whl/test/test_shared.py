
from generalpackager import Packager

import unittest


class TestGitHub(unittest.TestCase):
    def test_is_general(self):
        self.assertEqual(True, Packager().is_general())
        self.assertEqual(True, Packager().github.is_general())
        self.assertEqual(True, Packager().pypi.is_general())
        self.assertEqual(True, Packager().localrepo.is_general())
        self.assertEqual(True, Packager().localmodule.is_general())

        self.assertEqual(True, Packager("generalfile").is_general())
        self.assertEqual(True, Packager("generalfile").github.is_general())
        self.assertEqual(True, Packager("generalfile").pypi.is_general())
        self.assertEqual(True, Packager("generalfile").localrepo.is_general())
        self.assertEqual(True, Packager("generalfile").localmodule.is_general())

        self.assertEqual(False, Packager("pandas").is_general())
        self.assertEqual(False, Packager("pandas").github.is_general())
        self.assertEqual(False, Packager("pandas").pypi.is_general())
        self.assertEqual(False, Packager("pandas").localrepo.is_general())
        self.assertEqual(False, Packager("pandas").localmodule.is_general())


