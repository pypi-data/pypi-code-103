import unittest
from click.testing import CliRunner
import json
from dnastack import __main__ as dnastack_cli

from .utils import *
from .. import *


class TestCliDataConnectTablesCommand(unittest.TestCase):
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

    def test_tables_list(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack, ["dataconnect", "tables", "list"]
        )
        self.assertEqual(result.exit_code, 0)

        result_objects = json.loads(result.output)

        for item in result_objects:
            assert_has_property(self, item, "name")
            assert_has_property(self, item, "data_model")
            assert_has_property(self, item["data_model"], "$ref")

    def test_tables_get_table(self):
        table_info_result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["dataconnect", "tables", "get", TEST_DATA_CONNECT_VARIANTS_TABLE],
        )
        table_info_object = json.loads(table_info_result.output)

        self.assertEqual(table_info_result.exit_code, 0)

        assert_has_property(self, table_info_object, "name")
        assert_has_property(self, table_info_object, "description")
        assert_has_property(self, table_info_object, "data_model")
        assert_has_property(self, table_info_object["data_model"], "$id")
        assert_has_property(self, table_info_object["data_model"], "$schema")
        assert_has_property(self, table_info_object["data_model"], "description")

        for property in table_info_object["data_model"]["properties"]:
            assert_has_property(
                self, table_info_object["data_model"]["properties"][property], "format"
            )
            assert_has_property(
                self, table_info_object["data_model"]["properties"][property], "type"
            )
            assert_has_property(
                self,
                table_info_object["data_model"]["properties"][property],
                "$comment",
            )

    def test_tables_get_table_does_not_exist(self):
        table_info_result = self.runner.invoke(
            dnastack_cli.dnastack, ["dataconnect", "tables", "get", "some table name"]
        )

        self.assertEqual(table_info_result.exit_code, 1)
