import os
import unittest
from click.testing import CliRunner
import json
from dnastack import __main__ as dnastack_cli

from .utils import clear_config
from .. import *


class TestCliConfigCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.data_connect_url = TEST_DATA_CONNECT_URI
        self.wes_url = TEST_WES_URI
        self.wallet_url = TEST_AUTH_PARAMS["publisher"]["url"]
        self.refresh_token = TEST_WALLET_REFRESH_TOKEN["publisher"]
        clear_config()

    def test_cli_config_set_get(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["config", "set", "data_connect.url", self.data_connect_url],
        )

        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(
            dnastack_cli.dnastack, ["config", "get", "data_connect.url"]
        )

        self.assertEqual(result.exit_code, 0)

        self.assertEqual(result.output.strip(), self.data_connect_url)

    def test_cli_config_set_get_delimiter(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "config",
                "set",
                "data_connect|url",
                self.data_connect_url,
                "--delimiter",
                "|",
            ],
        )

        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["config", "get", "data_connect+url", "--delimiter", "+"],
        )

        self.assertEqual(result.exit_code, 0)

        self.assertEqual(result.output.strip(), self.data_connect_url)

    def test_cli_config_set_get_no_trailing_slash(self):

        no_slash_url = (
            self.data_connect_url[:-1]
            if self.data_connect_url[-1] == "/"
            else self.data_connect_url
        )

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["config", "set", "data_connect.url", no_slash_url],
        )

        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(
            dnastack_cli.dnastack, ["config", "get", "data_connect.url"]
        )

        self.assertEqual(result.exit_code, 0)

        self.assertEqual(result.output.strip(), no_slash_url + "/")

    def test_cli_config_get_bad_key(self):
        result = self.runner.invoke(dnastack_cli.dnastack, ["config", "get", "testKey"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("not an accepted configuration key", result.output)

    def test_cli_config_set_bad_key(self):
        result = self.runner.invoke(
            dnastack_cli.dnastack, ["config", "set", "testKey", "testValue"]
        )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("not an accepted configuration key", result.output)
        self.assertIn("accepted configuration keys", result.output.lower())

        # test for invalid keys within valid config
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["config", "set", "data_connect.testKey", "testValue"],
        )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("not an accepted configuration key", result.output.lower())

    def test_cli_config_list(self):

        self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "config",
                "set",
                "data_connect.url",
                self.data_connect_url,
            ],
        )

        self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "config",
                "set",
                "wes.url",
                self.wes_url,
            ],
        )

        # test config list
        result = self.runner.invoke(dnastack_cli.dnastack, ["config", "list"])

        result_object = json.loads(result.output)

        self.assertEqual(result_object["data_connect"]["url"], self.data_connect_url)
        self.assertEqual(result_object["wes"]["url"], self.wes_url)
