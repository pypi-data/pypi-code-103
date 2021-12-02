import os
import unittest
from click.testing import CliRunner
import json
import csv
from io import StringIO
from dnastack import __main__ as dnastack_cli

from .utils import *
from .. import *


class TestCliDataConnectQueryCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.data_connect_url = TEST_DATA_CONNECT_URI
        self.wallet_url = TEST_AUTH_PARAMS["publisher"]["url"]

        clear_config()
        set_cli_config(self.runner, "data_connect.url", self.data_connect_url)
        set_auth_params_for_service(
            self.runner,
            service="data-connect",
            auth_params=TEST_AUTH_PARAMS["publisher"],
        )
        set_cli_config(
            self.runner,
            f"oauth|{self.wallet_url}|scope",
            TEST_AUTH_SCOPES["publisher"],
            delimiter="|",
        )
        login_with_refresh_token_for_service(
            self.runner,
            service="data-connect",
            refresh_token=TEST_WALLET_REFRESH_TOKEN["publisher"],
        )

    def test_variant_query(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "dataconnect",
                "query",
                f"SELECT * from {TEST_DATA_CONNECT_VARIANTS_TABLE} LIMIT 5",
            ],
        )
        result_objects = json.loads(result.output)

        self.assertEqual(result.exit_code, 0)

        for item in result_objects:
            assert_has_property(self, item, "start_position")
            assert_has_property(self, item, "end_position")
            assert_has_property(self, item, "reference_bases")
            assert_has_property(self, item, "alternate_bases")
            assert_has_property(self, item, "sequence_accession")

    def test_csv_query(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "dataconnect",
                "query",
                f"SELECT * FROM {TEST_DATA_CONNECT_VARIANTS_TABLE} LIMIT 5",
                "-f",
                "csv",
            ],
        )
        csv_string = StringIO(result.output)
        csv_results = csv.reader(csv_string)

        self.assertEqual(result.exit_code, 0)

        header_row = next(csv_results)

        # tests that headers are present
        self.assertIn("start_position", header_row)
        self.assertIn("end_position", header_row)
        self.assertIn("reference_bases", header_row)
        self.assertIn("alternate_bases", header_row)
        self.assertIn("sequence_accession", header_row)

        for item in csv_results:
            self.assertEqual(len(item), len(header_row))

    def test_drs_url_query(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "dataconnect",
                "query",
                f"SELECT drs_url FROM {TEST_DATA_CONNECT_FILES_TABLE} LIMIT 5",
            ],
        )
        result_objects = json.loads(result.output)

        self.assertEqual(result.exit_code, 0)

        for item in result_objects:
            assert_has_property(self, item, "drs_url")

    def test_incorrect_column_query(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "dataconnect",
                "query",
                f"SELECT imaginary_field FROM {TEST_DATA_CONNECT_VARIANTS_TABLE} LIMIT 5",
            ],
        )
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Column 'imaginary_field' cannot be resolved", result.output)

    def test_broken_query(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack, ["dataconnect", "query", "broken_query"]
        )
        self.assertEqual(result.exit_code, 1)
