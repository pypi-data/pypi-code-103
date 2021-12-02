import json
import os
from typing import Optional

import requests as req

from dnastack.client.utils import get_access_token_for_wes_client
from requests import RequestException


def get_service_info(
    wes_url, oauth_token: Optional[dict] = None, auth_params: Optional[dict] = None
):
    system_state_counts = None

    if oauth_token:
        try:
            list_of_workflows = get_list_of_workflows_executed(
                wes_url, oauth_token, auth_params
            )

            system_state_counts = {}

            for run in list_of_workflows["runs"]:
                if system_state_counts.get(run["state"], None) is None:
                    system_state_counts[run["state"]] = 1
                else:
                    system_state_counts[run["state"]] = (
                        system_state_counts[run["state"]] + 1
                    )

        except RequestException:
            # if it's anything requests-related, then we ignore
            pass
        except Exception as e:
            raise e

    response = req.get(wes_url + "ga4gh/wes/v1/service-info").json()

    if system_state_counts is not None:
        response["system_state_counts"] = system_state_counts

    return response


def submit_workflow(
    wes_url,
    workflow_url,
    oauth_token: dict,
    auth_params: dict,
    attachment_files: list = None,
    input_params_file=None,
    engine_param=None,
    engine_params_file=None,
    tag=None,
    tags_file=None,
):
    attachment_file_contents = []
    input_params = None
    engine_params_file_contents = None
    tags_file_contents = None

    for attachment_file in attachment_files:
        with open(attachment_file, "rb") as file:
            attachment_file_contents.append(file.read())
            file.close()

    if input_params_file:
        with open(input_params_file, "r") as file:
            input_params = file.read()
            file.close()

    if engine_params_file:
        with open(engine_params_file, "r") as file:
            engine_params_file_contents = file.read()
            file.close()

    if tags_file:
        with open(tags_file, "r") as file:
            tags_file_contents = file.read()
            file.close()

    url = wes_url + "ga4gh/wes/v1/runs"

    files = [("workflow_url", (None, workflow_url, "text/plain"))]

    for attachment_file, attachment_file_content in zip(
        attachment_files, attachment_file_contents
    ):
        files.append(
            (
                "workflow_attachment",
                (
                    os.path.basename(attachment_file),
                    attachment_file_content,
                    "application/octet-stream",
                ),
            )
        )

    if input_params:
        files.append(("workflow_params", (None, input_params, "application/json")))

    if engine_param:
        files.append(
            ("workflow_engine_parameters", (None, engine_param, "application/json"))
        )

    if engine_params_file_contents:
        files.append(
            (
                "workflow_engine_parameters",
                (None, engine_params_file_contents, "application/json"),
            )
        )

    if tag:
        files.append(("tags", (None, tag, "application/json")))

    if tags_file_contents:
        files.append(("tags", (None, tags_file_contents, "application/json")))

    access_token = get_access_token_for_wes_client(oauth_token, auth_params)
    headers = {"Authorization": f"Bearer {access_token}"}

    return req.post(url, files=files, headers=headers).json()


def get_list_of_workflows_executed(
    wes_url, oauth_token: dict, auth_params: dict, page_size=None, next_page_token=None
):
    url = wes_url + "ga4gh/wes/v1/runs"
    access_token = get_access_token_for_wes_client(oauth_token, auth_params)
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {}

    if page_size:
        params["page_size"] = page_size

    if next_page_token:
        params["page_token"] = next_page_token

    if not page_size and not next_page_token:
        result = {"runs": []}
        while True:
            response = req.get(url, headers=headers, params=params).json()
            result["runs"].extend(response["runs"])

            if response.get("next_page_token", None) is not None:
                params["page_token"] = response["next_page_token"]
            else:
                return result
    else:
        return req.get(url, headers=headers, params=params).json()


def get_run_details(
    wes_url, run_id, oauth_token: dict, auth_params: dict, status_only=False
):
    url = wes_url + "ga4gh/wes/v1/runs/" + run_id
    access_token = get_access_token_for_wes_client(oauth_token, auth_params)
    headers = {"Authorization": f"Bearer {access_token}"}

    if status_only:
        url = url + "/status"

    return req.get(url, headers=headers).json()


def cancel_run(wes_url, run_id, oauth_token: dict, auth_params: dict):
    url = wes_url + "ga4gh/wes/v1/runs/" + run_id + "/cancel"
    access_token = get_access_token_for_wes_client(oauth_token, auth_params)
    headers = {"Authorization": f"Bearer {access_token}"}

    return req.post(url, headers=headers).json()


def get_run_logs(
    wes_url,
    run_id,
    oauth_token: dict,
    auth_params: dict,
    stdout=False,
    stderr=False,
    url=None,
    task=None,
    index=0,
):
    if (not stdout) and (not stderr) and (not url):
        raise RuntimeError(
            "One of the following options must be used: stderr stdout url"
        )
    elif stdout and (not task):
        raise RuntimeError("stdout option requires following argument: task")

    access_token = get_access_token_for_wes_client(oauth_token, auth_params)
    headers = {"Authorization": f"Bearer {access_token}"}

    if url:
        return req.get(url, headers=headers).content

    url = wes_url + "ga4gh/wes/v1/runs/" + run_id + "/logs"

    if task:
        url = url + "/task/" + task + "/" + str(index)

    if stderr:
        url = url + "/stderr"
    elif stdout:
        url = url + "/stdout"

    return req.get(url, headers=headers).content
