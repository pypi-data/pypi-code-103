from unittest import TestCase
from requests import get
from json import loads as json_loads
from database_connector import __version__, __name__


class TestVersion(TestCase):
    def test_check_version(self):
        json_response = json_loads(get(f"https://pypi.org/pypi/{__name__}/json").text)
        self.assertIsNone(json_response['releases'].get(__version__))
