import time
import unittest
import warnings

from click.testing import CliRunner
import json
from dnastack import __main__ as dnastack_cli
from .utils import *
from .. import *

unittest.TestLoader.sortTestMethodsUsing = None


def assert_has_property(self, obj, attribute):
    self.assertTrue(
        attribute in obj,
        msg="obj lacking an attribute. obj: %s, intendedAttribute: %s"
        % (obj, attribute),
    )


class TestCliWesRunsCommand(unittest.TestCase):
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

    def test_wes_runs_execute(self):
        self.__execute_workflow()

    def test_wes_runs_execute_multiple_attachments(self):
        with open(TEST_WDL_MULTI_GREETING, "r") as main_wdl:
            wdl_main_file_path = self.__create_file("main.wdl", main_wdl.read())

        with open(TEST_WDL_MULTI_GREETING, "r") as greeting_wdl:
            wdl_greeting_attachment_file = self.__create_file(
                "greeting.wdl", greeting_wdl.read()
            )

        with open(TEST_WDL_MULTI_FAREWELL, "r") as farewell_wdl:
            wdl_farewell_attachment_file = self.__create_file(
                "farewell.wdl", farewell_wdl.read()
            )

        wdl_input_param_file_path = self.__create_file(
            "input.json", TEST_WDL_INPUT_PARAM_CONTENTS
        )
        wdl_engine_param_file_path = self.__create_file(
            "engine.json", TEST_WDL_ENGINE_PARAM_CONTENTS
        )
        wdl_tag_file_path = self.__create_file("tag.json", TEST_WDL_TAG_CONTENTS)
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "wes",
                "runs",
                "execute",
                "--workflow-url",
                "main.wdl",
                "--attachment",
                wdl_main_file_path,
                "--attachment",
                wdl_greeting_attachment_file,
                "--attachment",
                wdl_farewell_attachment_file,
                "--inputs-file",
                wdl_input_param_file_path,
                "--engine-parameters-file",
                wdl_engine_param_file_path,
                "--tags-file",
                wdl_tag_file_path,
            ],
        )

        self.assertEqual(
            result.exit_code,
            0,
            msg=f"wes runs execute failed with code {result.exit_code} ({result.output})",
        )

        result_objects = json.loads(result.output)
        assert_has_property(self, result_objects, "run_id")

        os.remove(wdl_main_file_path)
        os.remove(wdl_greeting_attachment_file)
        os.remove(wdl_farewell_attachment_file)
        os.remove(wdl_input_param_file_path)
        os.remove(wdl_engine_param_file_path)
        os.remove(wdl_tag_file_path)

        return result_objects

    def test_wes_runs_list(self):
        self.__execute_workflow()
        self.__execute_workflow()
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["wes", "runs", "list", "--page-size", 1],
        )
        output = result.output.split("wes runs list")

        result_objects = json.loads(output[0])
        self.assertEqual(result.exit_code, 0)
        assert_has_property(self, result_objects, "runs")
        assert_has_property(self, result_objects, "next_page_token")
        self.assertTrue(len(result_objects["runs"]) == 1)
        self.assertTrue(
            f" --page-token {result_objects['next_page_token']}\n" == output[1]
        )

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["wes", "runs", "list", "--page-token", result_objects["next_page_token"]],
        )
        output = result.output.split("wes runs list")

        result_objects = json.loads(output[0])
        self.assertEqual(result.exit_code, 0)
        assert_has_property(self, result_objects, "runs")
        self.assertTrue(len(result_objects["runs"]) == 1)

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["wes", "runs", "list", "--all"],
        )
        result_objects = json.loads(result.output)
        self.assertEqual(result.exit_code, 0)
        assert_has_property(self, result_objects, "runs")
        self.assertTrue(len(result_objects["runs"]) > 0)
        self.assertTrue("next_page_token" not in result_objects)

    def test_run_get(self):
        self.__execute_workflow()
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["wes", "runs", "list", "--page-size", 1],
        )
        output = result.output.split("wes runs list")

        result_objects = json.loads(output[0])
        run_id = result_objects["runs"][0]["run_id"]

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["wes", "run", "get", run_id],
        )

        self.assertEqual(result.exit_code, 0)

        result_objects = json.loads(result.output)

        assert_has_property(self, result_objects, "run_id")
        assert_has_property(self, result_objects, "request")
        assert_has_property(self, result_objects, "state")
        assert_has_property(self, result_objects, "run_log")
        assert_has_property(self, result_objects, "task_logs")
        assert_has_property(self, result_objects, "outputs")

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["wes", "run", "get", run_id, "--status"],
        )

        result_objects = json.loads(result.output)
        self.assertEqual(result.exit_code, 0)
        assert_has_property(self, result_objects, "run_id")
        assert_has_property(self, result_objects, "state")
        self.assertTrue("request" not in result_objects)
        self.assertTrue("run_log" not in result_objects)
        self.assertTrue("task_logs" not in result_objects)
        self.assertTrue("outputs" not in result_objects)

    def test_wes_run_cancel(self):
        result = self.__execute_workflow()
        run_id = result["run_id"]
        time.sleep(10)
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            ["wes", "run", "cancel", run_id],
        )

        self.assertEqual(result.exit_code, 0)

        result_objects = json.loads(result.output)

        assert_has_property(self, result_objects, "run_id")

    @unittest.skip(
        "Disabling temporarily since WES service is inconsistent and fails this test due to timeout"
    )
    def test_wes_run_logs(self):
        result = self.__execute_workflow()
        run_id = result["run_id"]
        time.sleep(5)
        time_remaining = 240

        run_status = self.runner.invoke(
            dnastack_cli.dnastack,
            ["wes", "run", "get", run_id, "--status"],
        )
        run_status = json.loads(run_status.output)

        while run_status.get("state") in ("INITIALIZING", "RUNNING"):
            if time_remaining <= 0:
                self.runner.invoke(
                    dnastack_cli.dnastack,
                    ["wes", "run", "cancel", run_id],
                )
                self.fail("The workflow timed out")
            time_remaining -= 10
            time.sleep(10)
            run_status = self.runner.invoke(
                dnastack_cli.dnastack,
                ["wes", "run", "get", run_id, "--status"],
            )
            run_status = json.loads(run_status.output)

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "wes",
                "run",
                "logs",
                run_id,
                "--stdout",
                "--task",
                "hello_world.first_greeting",
            ],
        )

        self.assertEqual(result.output, "Hello World, my name is Patrick!\n\n")
        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "wes",
                "run",
                "logs",
                run_id,
                "--stdout",
                "--task",
                "hello_world.say_greeting",
                "--index",
                1,
            ],
        )
        print(result.output)

        self.assertEqual(result.output, "Hello World, my name is Patrick!\n\n")
        self.assertEqual(result.exit_code, 0)

        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "wes",
                "run",
                "logs",
                run_id,
                "--url",
                TEST_WES_URI
                + "ga4gh/wes/v1/runs/"
                + run_id
                + "/logs/task/hello_world.say_greeting/0/stdout",
            ],
        )

        self.assertEqual(result.output, "Hello World, my name is Patrick!\n\n")
        self.assertEqual(result.exit_code, 0)

    @staticmethod
    def __create_file(file_name, contents):
        with open(file_name, "w") as file:
            file.write(contents)
            return os.path.realpath(file.name)

    def __execute_workflow(self):
        wdl_file_path = self.__create_file("workflow.wdl", TEST_WDL_FILE_CONTENTS)
        wdl_input_param_file_path = self.__create_file(
            "input.json", TEST_WDL_INPUT_PARAM_CONTENTS
        )
        wdl_engine_param_file_path = self.__create_file(
            "engine.json", TEST_WDL_ENGINE_PARAM_CONTENTS
        )
        wdl_tag_file_path = self.__create_file("tag.json", TEST_WDL_TAG_CONTENTS)
        result = self.runner.invoke(
            dnastack_cli.dnastack,
            [
                "wes",
                "runs",
                "execute",
                "--workflow-url",
                "workflow.wdl",
                "--attachment",
                wdl_file_path,
                "--inputs-file",
                wdl_input_param_file_path,
                "--engine-parameters-file",
                wdl_engine_param_file_path,
                "--tags-file",
                wdl_tag_file_path,
            ],
        )

        self.assertEqual(
            result.exit_code,
            0,
            msg=f"wes runs execute failed with code {result.exit_code} ({result.output})",
        )

        result_objects = json.loads(result.output)

        assert_has_property(self, result_objects, "run_id")

        os.remove(wdl_file_path)
        os.remove(wdl_input_param_file_path)
        os.remove(wdl_engine_param_file_path)
        os.remove(wdl_tag_file_path)

        return result_objects
