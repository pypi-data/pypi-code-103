import unittest
import warnings

from click.testing import CliRunner
import json
from dnastack import __main__ as dnastack_cli
from .. import *
from .utils import *


class TestCliWesCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.wes_url = TEST_WES_URI
        self.wallet_url = TEST_AUTH_PARAMS["wes"]["url"]

        clear_config()
        set_cli_config(self.runner, "wes.url", self.wes_url)
        set_auth_params_for_service(
            self.runner, service="wes", auth_params=TEST_AUTH_PARAMS["wes"]
        )
        set_cli_config(
            self.runner,
            f"oauth|{self.wallet_url}|scope",
            TEST_AUTH_SCOPES["wes"],
            delimiter="|",
        )
        login_with_refresh_token_for_service(
            self.runner, service="wes", refresh_token=TEST_WALLET_REFRESH_TOKEN["wes"]
        )

    def test_wes_info_with_auth(self):
        result = self.runner.invoke(dnastack_cli.dnastack, ["wes", "info"])
        result_objects = json.loads(result.output)

        self.assertEqual(result.exit_code, 0)

        assert_has_property(self, result_objects, "workflow_type_versions")
        assert_has_property(self, result_objects, "supported_wes_versions")
        assert_has_property(self, result_objects, "supported_filesystem_protocols")
        assert_has_property(self, result_objects, "workflow_engine_versions")
        assert_has_property(self, result_objects, "system_state_counts")
