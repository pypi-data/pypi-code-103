import os
import time
import unittest
import pathlib
from dnastack import PublisherClient, ServiceType
from .. import *
import json


def create_file_from_str(file_name: str, contents: str):
    with open(file_name, "w") as file:
        file.write(contents)
        return os.path.realpath(file.name)


def execute_workflow(publisher_client: PublisherClient):
    wdl_file_path = create_file_from_str("workflow.wdl", TEST_WDL_FILE_CONTENTS)
    wdl_input_param_file_path = create_file_from_str(
        "input.json", TEST_WDL_INPUT_PARAM_CONTENTS
    )
    wdl_engine_param_file_path = create_file_from_str(
        "engine.json", TEST_WDL_ENGINE_PARAM_CONTENTS
    )
    wdl_tag_file_path = create_file_from_str("tag.json", TEST_WDL_TAG_CONTENTS)

    result = publisher_client.wes.execute(
        "workflow.wdl",
        attachment_files=[wdl_file_path],
        input_params_file=wdl_input_param_file_path,
        engine_params_file=wdl_engine_param_file_path,
        tags_file=wdl_tag_file_path,
    )

    if result is None or "run_id" not in result.keys():
        raise Exception("Could not execute workflow")

    os.remove(wdl_file_path)
    os.remove(wdl_input_param_file_path)
    os.remove(wdl_engine_param_file_path)
    os.remove(wdl_tag_file_path)

    return result


class TestCliWesCommand(unittest.TestCase):
    def setUp(self):
        self.publisher_client = PublisherClient(
            email=TEST_WALLET_EMAIL,
            personal_access_token=TEST_WALLET_PERSONAL_ACCESS_TOKEN_PUBLISHER,
            wes_url=TEST_WES_URI,
            auth_params=TEST_AUTH_PARAMS["wes"],
        )
        self.wes_url = TEST_WES_URI
        self.publisher_client.auth.set_refresh_token_for_service(
            service_type=ServiceType.WES, token=TEST_WALLET_REFRESH_TOKEN["wes"]
        )
        self.publisher_client.auth.oauth[TEST_AUTH_PARAMS["wes"]["url"]][
            "scope"
        ] = TEST_AUTH_SCOPES["wes"]
        self.publisher_client.auth.refresh_token_for_service(
            service_type=ServiceType.WES
        )

    def test_wes_info_with_auth(self):
        result = self.publisher_client.wes.info()

        self.assertIsNotNone(result)

        self.assertIn("workflow_type_versions", result.keys())
        self.assertIn("supported_wes_versions", result.keys())
        self.assertIn("supported_filesystem_protocols", result.keys())
        self.assertIn("workflow_engine_versions", result.keys())
        self.assertIn("system_state_counts", result.keys())

    def test_wes_runs_execute(self):
        workflow = execute_workflow(self.publisher_client)
        self.assertIsNotNone(workflow)

    def test_wes_runs_list(self):
        execute_workflow(self.publisher_client)
        execute_workflow(self.publisher_client)
        result = self.publisher_client.wes.list()

        self.assertIsNotNone(result)
        self.assertIn("runs", result.keys())

    def test_run_get(self):
        execute_workflow(self.publisher_client)
        runs = self.publisher_client.wes.list()
        run_id = runs["runs"][0]["run_id"]

        run_info = self.publisher_client.wes.get(run_id)

        self.assertIsNotNone(run_info)
        self.assertIn("run_id", run_info.keys())
        self.assertIn("request", run_info.keys())
        self.assertIn("state", run_info.keys())
        self.assertIn("run_log", run_info.keys())
        self.assertIn("task_logs", run_info.keys())
        self.assertIn("outputs", run_info.keys())

        run_info = self.publisher_client.wes.get(run_id, status_only=True)

        self.assertIsNotNone(run_info)
        self.assertIn("run_id", run_info.keys())
        self.assertIn("state", run_info.keys())

        self.assertNotIn("request", run_info.keys())
        self.assertNotIn("run_log", run_info.keys())
        self.assertNotIn("task_logs", run_info.keys())
        self.assertNotIn("outputs", run_info.keys())

    def test_wes_run_cancel(self):
        workflow = execute_workflow(self.publisher_client)
        run_id = workflow["run_id"]
        time.sleep(10)
        result = self.publisher_client.wes.cancel(run_id)

        self.assertIsNotNone(result)
        self.assertIn("run_id", result.keys())

    @unittest.skip(
        "Disabling temporarily since WES service is inconsistent and fails this test due to timeout"
    )
    def test_wes_run_logs(self):
        workflow = execute_workflow(self.publisher_client)
        run_id = workflow["run_id"]

        time.sleep(5)
        time_remaining = 240

        run_status = self.publisher_client.wes.get(run_id, status_only=True)

        while run_status.get("state") in ("INITIALIZING", "RUNNING"):
            if time_remaining <= 0:
                self.publisher_client.wes.cancel(run_id)
                self.fail("The workflow timed out")
            time_remaining -= 10
            time.sleep(10)
            run_status = self.publisher_client.wes.get(run_id, status_only=True)

        result = self.publisher_client.wes.run_logs(
            run_id=run_id, stdout=True, task="hello_world.first_greeting"
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.decode("utf-8"), "Hello World, my name is Patrick!\n")

        result = self.publisher_client.wes.run_logs(
            run_id=run_id, stdout=True, task="hello_world.first_greeting", index=0
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.decode("utf-8"), "Hello World, my name is Patrick!\n")

        result = self.publisher_client.wes.run_logs(
            run_id=run_id,
            url=f"{TEST_WES_URI}ga4gh/wes/v1/runs/{run_id}/logs/task/hello_world.say_greeting/0/stdout",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.decode("utf-8"), "Hello World, my name is Patrick!\n")
