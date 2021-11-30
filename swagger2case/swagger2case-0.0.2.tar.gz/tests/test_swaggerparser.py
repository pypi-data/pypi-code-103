import unittest
import os
import json
import shutil
from swagger2case.core import SwaggerParser


class TestParser(unittest.TestCase):

    def setUp(self):
        self.swagger_parser = SwaggerParser("tests/data/swaggerApi.json")

    def test_init(self):
        self.assertEqual(self.swagger_parser.swagger_testcase_file, "tests/data/swaggerApi.json")

    def test_read_swagger_data(self):
        with open("tests/data/swaggerApi.json", encoding='utf-8', mode='r') as f:
            content = json.load(f)
        other_content = self.swagger_parser.read_swagger_data()
        self.assertEqual(content, other_content)
    
    def test_parse_data(self):
        result, name = self.swagger_parser.parse_data()
        self.assertEqual(len(result), 3)
    
    def test_save(self):
        result, name = self.swagger_parser.parse_data()
        self.swagger_parser.save(result, name, name=name)
        shutil.rmtree(name)
