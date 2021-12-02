import unittest
from click.testing import CliRunner
import json
from dnastack import __main__ as dnastack_cli

from .utils import assert_has_property, set_cli_config
from .. import *


class TestCliCollectionsCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.collections_url = TEST_COLLECTIONS_URI
        set_cli_config(self.runner, "collections.url", self.collections_url)

    def test_collections_list(self):
        result = self.runner.invoke(dnastack_cli.dnastack, ["collections", "list"])
        result_objects = json.loads(result.output)

        self.assertEqual(result.exit_code, 0)

        for item in result_objects:
            assert_has_property(self, item, "name")
            assert_has_property(self, item, "id")

    def test_collections_tables_list(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["collections", "tables", "list", TEST_COLLECTION_NAME],
        )
        result_objects = json.loads(result.output)

        self.assertEqual(result.exit_code, 0)

        for item in result_objects:
            assert_has_property(self, item, "name")
            assert_has_property(self, item, "data_model")
            assert_has_property(self, item["data_model"], "$ref")

    def test_collections_tables_list_bad_collection(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack, ["collections", "tables", "list", "bad-collection"]
        )
        result_objects = json.loads(result.output)

        self.assertEqual(result.exit_code, 0)

        self.assertEqual(len(result_objects), 0)

    def test_collections_query(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["collections", "query", TEST_COLLECTION_NAME, TEST_COLLECTION_QUERY],
        )
        result_objects = json.loads(result.output)

        self.assertEqual(result.exit_code, 0)

        self.assertGreater(len(result_objects), 0)

        for item in result_objects:
            assert_has_property(self, item, "start_position")
            assert_has_property(self, item, "sequence_accession")

    def test_collections_query_bad_query(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "collections",
                "query",
                TEST_COLLECTION_NAME,
                "SELECT badfield FROM badtable",
            ],
        )

        self.assertNotEqual(result.exit_code, 0)
        # make sure it gives the collection name and url
        self.assertIn(TEST_COLLECTION_NAME, result.output)
        self.assertIn(TEST_COLLECTIONS_URI, result.output)

    def test_collections_query_bad_collection(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["collections", "query", "badcollection", "SELECT * FROM table"],
        )

        self.assertNotEqual(result.exit_code, 0)

        # make sure it gives the collection name and url
        self.assertIn("badcollection", result.output)
        self.assertIn(TEST_COLLECTIONS_URI, result.output)
