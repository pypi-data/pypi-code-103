import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import unittest
from expdb import Authenticate

class TestAuthenticate(unittest.TestCase):
    def test_auth(self):
        RESULT = Authenticate(
            username = "root",
            password = "root",
            database = "test"
        ).auth()
        self.assertEqual(RESULT, True)
