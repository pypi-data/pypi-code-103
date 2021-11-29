
from generalpackager.api.github import GitHub

import unittest


class TestGitHub(unittest.TestCase):
    """ Skipped tests:
        set_website()
        set_topics()
        set_description()
    """
    def test_exists(self):
        self.assertEqual(True, GitHub("generalpackager").exists())

    def test_topics(self):
        github = GitHub("generalpackager")
        self.assertTrue(github.get_topics())

    def test_get_owners_packages(self):
        github = GitHub()
        self.assertEqual(set(), {"generallibrary", "generalfile", "generalvector", "generalpackager"}.difference(github.get_owners_packages()))

        github = GitHub(owner="pandas-dev")
        self.assertEqual(True, "pandas" in github.get_owners_packages())

    def test_get_website(self):
        github = GitHub("generalpackager")
        self.assertEqual(True, "pypi" in github.get_website())

    def test_get_description(self):
        github = GitHub("generalpackager")
        self.assertEqual(True, len(github.get_description()) > 5)


