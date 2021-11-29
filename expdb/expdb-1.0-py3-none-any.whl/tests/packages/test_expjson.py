import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import shutil
import unittest
from expdb import JSON

class TestExpJSON(unittest.TestCase):
    def test_exportone(self):
        PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        RESULT = JSON(
            username = "root",
            password = "root",
            database = "test"
        ).exportone(
            table = "users",
            path = PATH
        )
        self.assertEqual(RESULT, True)
        os.remove(os.path.join(PATH, "test.users.json"))

    def test_exportmany(self):
        PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        RESULT = JSON(
            username = "root",
            password = "root",
            database = "test"
        ).exportmany(
            tables = ["users"],
            path = PATH
        )
        self.assertEqual(RESULT, True)
        shutil.rmtree(os.path.join(PATH, "test"))

    def test_exportall(self):
        PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        RESULT = JSON(
            username = "root",
            password = "root",
            database = "test"
        ).exportall(path = PATH)
        self.assertEqual(RESULT, True)
        shutil.rmtree(os.path.join(PATH, "test"))
