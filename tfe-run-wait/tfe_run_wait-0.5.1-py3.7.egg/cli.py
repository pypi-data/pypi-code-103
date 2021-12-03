import argparse
import os
from sys import stderr
from time import sleep, time
from typing import Iterable, List, Optional

import requests
from requests import Response

from tfe_run_wait.argument_types import EnvDefault
from tfe_run_wait.logger import log

_tfe_api_token = os.getenv("TFE_API_TOKEN")


def _post(path: str, params: dict = {}, data: dict = {}):
    hdrs = {
        "Authorization": f"Bearer {_tfe_api_token}",
        "content-type": "application/vnd.api+json",
    }

    if path.startswith("/api/") or path.startswith("api/"):
        url = f'https://app.terraform.io/{path.lstrip("/")}'
    else:
        url = f"https://app.terraform.io/api/v2/{path}"

    log.debug("post %s, %s, %s", url, params, data)
    r = requests.post(url, headers=hdrs, params=params, json=data)
    if r.status_code not in [200, 201, 202]:
        raise TFEError(r)


class TFEError(Exception):
    def __init__(self, response: Response):
        try:
            self.errors = response.json().get("errors", [])
        except:
            self.errors = [{"status": response.status_code, "title": response.text}]

    def __str__(self):
        return "\n".join(
            map(lambda e: "{}: {}".format(e.get("status"), e.get("title")), self.errors)
        )

    @property
    def status(self):
        return self.errors[0].get("status") if self.errors else "500"

    @property
    def title(self):
        return self.errors[0].get("status") if self.errors else "unknown"


def _get(path: str, params: dict = {}) -> Optional[dict]:
    hdrs = {"Authorization": f"Bearer {_tfe_api_token}"}

    if path.startswith("/api/") or path.startswith("api/"):
        url = f'https://app.terraform.io/{path.lstrip("/")}'
    else:
        url = f"https://app.terraform.io/api/v2/{path}"

    log.debug("get %s, %s", url, params)
    r = requests.get(url, headers=hdrs, params=params)
    if r.status_code == 200:
        return r.json()["data"]
    elif r.status_code == 404:
        return None
    else:
        raise TFEError(r)


def _list(path: str, headers: dict = {}, params: dict = {}) -> Iterable[dict]:
    prms = {"page[size]": 100}
    hdrs = {"Authorization": f"Bearer {_tfe_api_token}"}
    if headers:
        hdrs.update(headers)
    if params:
        prms.update(params)

    if path.startswith("api/"):
        url = f"https://app.terraform.io/{path}"
    else:
        url = f"https://app.terraform.io/api/v2/{path}"

    log.debug("get %s, %s", url, params)
    r = requests.get(url, headers=hdrs, params=prms)
    while r.status_code == 200:
        response = r.json()
        next_page = response.get("links", {}).get("next")
        for d in response["data"]:
            yield d

        if next_page:
            r = requests.get(next_page, headers=hdrs)
        else:
            return

    if r.status_code not in (200, 404):
        raise TFEError(r)


def find_run_for_commit(workspace: dict, url: str, commit_sha: str) -> Optional[dict]:
    for run in _list(f'workspaces/{workspace["id"]}/runs'):
        configuration_version_id = (
            run.get("relationships", {})
            .get("configuration-version", {})
            .get("data", {})
            .get("id")
        )
        if configuration_version_id:
            ingress_attributes = _get(
                f"configuration-versions/{configuration_version_id}/ingress-attributes"
            )
            if ingress_attributes:
                ia_clone_url = ingress_attributes.get("attributes", {}).get("clone-url")
                ia_commit_sha = ingress_attributes.get("attributes", {}).get(
                    "commit-sha"
                )
                if ia_clone_url == url and ia_commit_sha == commit_sha:
                    log.info(f"found run {get_workspace_run_ui_url(workspace, run)} for commit {commit_sha[0:7]}")
                    return run
    return None


def get_apply(run: dict) -> Optional[dict]:
    apply_link = (
        run.get("relationships", {}).get("apply", {}).get("links", {}).get("related")
    )
    return _get(apply_link)


def get_plan(run: dict) -> Optional[dict]:
    plan_id = (
        run.get("relationships", {}).get("plan", {}).get("links", {}).get("related")
    )
    return _get(plan_id)


def show_plan(run: dict):
    plan = get_plan(run)
    if plan:
        url = plan.get("attributes", {}).get("log-read-url")
        if url:
            r = requests.get(url)
            if r.status_code == 200:
                stderr.write(r.text)


def show_apply(run: dict):
    plan = get_apply(run)
    if plan:
        url = plan.get("attributes", {}).get("log-read-url")
        if url:
            r = requests.get(url)
            if r.status_code == 200:
                stderr.write(r.text)


def get_workspace_run_ui_url(workspace: dict, run: dict):
    run_id = run["id"]
    workspace_name = workspace["attributes"]["name"]
    organization = workspace["relationships"]["organization"]["data"]["id"]
    return f"https://app.terraform.io/app/{organization}/workspaces/{workspace_name}/runs/{run_id}"


def wait_until(
    workspace: dict,
    wait_for_status: List[str],
    clone_url: str,
    commit_sha: str,
    maximum_wait_time_in_seconds: int,
) -> (int, dict):
    run_id = None
    workspace_name = workspace["attributes"]["name"]

    now = start_time = time()
    while (now - start_time) < maximum_wait_time_in_seconds:
        if not run_id:
            run = find_run_for_commit(workspace, clone_url, commit_sha)

        else:
            run = _get(f"/api/v2/runs/{run_id}")

        if run:
            run_id = run["id"]
            status = run.get("attributes").get("status")
            if status in wait_for_status:
                log.info(
                    "%s in workspace %s has reached state %s",
                    run_id,
                    workspace_name,
                    status,
                )
                return 0, run
            elif status in (
                "discarded",
                "errored",
                "canceled",
                "force_canceled",
                "planned_and_finished",
                "applied",
            ):
                log.error(
                    "%s in workspace %s has status %s and can no longer reach the desired status of %s",
                    run_id,
                    workspace_name,
                    status,
                    ", ".join(wait_for_status),
                )
                return 1, run
            else:
                log.info(
                    "%s in workspace %s in status %s, waited %ss",
                    run_id,
                    workspace_name,
                    status,
                    int(time() - start_time),
                )
                sleep(10)
        else:
            log.info(
                "waiting %ss for a run in workspace %s for commit %s in %s to appear",
                int(time() - start_time),
                workspace_name,
                commit_sha[0:7],
                clone_url,
            )
            sleep(10)
        now = time()

    if run_id:
        log.error(
            "timed out after %ss waiting for %s in workspace %s to reach state %s",
            int(time() - start_time),
            run_id,
            workspace_name,
            ", ".join(wait_for_status),
        )
    else:
        log.error(
            "time out while waiting for a run in workspace %s for commit %s in %s to appear",
            run_id,
            workspace_name,
            commit_sha[0:7],
            clone_url,
        )
    return 1, run


def _get_org_and_workspace(parser, args) -> (dict, dict):
    global _tfe_api_token
    if args.token:
        _tfe_api_token = args.token

    org = _get(f"organizations/{args.organization}")
    if not org:
        parser.error(f"unknown organization {args.organization}.")

    workspace = _get(f"organizations/{args.organization}/workspaces/{args.workspace}")
    if not workspace:
        parser.error(
            f"workspace {args.workspace} is unknown in organization {args.organization}."
        )
    return (org, workspace)


def _wait():
    parser = argparse.ArgumentParser(
        description="wait for TFE run to reach specified state."
    )
    parser.add_argument(
        "--token",
        action=EnvDefault,
        envvar="TFE_API_TOKEN",
        help="Terraform Enterprise access token, default from TFE_API_TOKEN",
    )

    parser.add_argument("--organization", required=True, help="of the workspace")
    parser.add_argument("--workspace", required=True, help="to inspect runs for")
    parser.add_argument(
        "--clone-url", required=True, help="of source repository for the run"
    )
    parser.add_argument(
        "--commit-sha", required=True, help="of commit which initiated the run"
    )
    parser.add_argument(
        "--wait-for-status",
        required=False,
        default=["applied", "planned_and_finished"],
        help="wait state to reach",
        action="append",
    )
    parser.add_argument(
        "--maximum-wait-time",
        required=False,
        type=int,
        default=45 * 60,
        help="for state to be reached in minutes, default 45",
    )
    args = parser.parse_args()
    org, workspace = _get_org_and_workspace(parser, args)

    log.info(
        f"waiting for run in {args.organization}:{args.workspace} for commit {args.commit_sha[0:7]} in repository {args.clone_url}"
    )
    result, run = wait_until(
        workspace,
        args.wait_for_status,
        args.clone_url,
        args.commit_sha,
        args.maximum_wait_time * 60,
    )

    if run:
        show_plan(run)

    return result


def _apply():
    parser = argparse.ArgumentParser(description="a planned TFE run.")
    parser.add_argument(
        "--token",
        action=EnvDefault,
        envvar="TFE_API_TOKEN",
        help="Terraform Enterprise access token, default from TFE_API_TOKEN",
    )

    parser.add_argument("--organization", required=True, help="of the workspace")
    parser.add_argument("--workspace", required=True, help="to inspect runs for")
    parser.add_argument(
        "--clone-url", required=True, help="of source repository for the run"
    )
    parser.add_argument(
        "--commit-sha", required=True, help="of commit which initiated the run"
    )
    parser.add_argument(
        "--maximum-wait-time",
        required=False,
        type=int,
        default=45 * 60,
        help="for state to be reached in minutes, default 45 (min)",
    )
    parser.add_argument("--comment", required=True, help="to include with the apply")

    args = parser.parse_args()
    org, workspace = _get_org_and_workspace(parser, args)

    log.info(
        f"apply run in {args.organization}:{args.workspace} for commit {args.commit_sha[0:7]} in repository {args.clone_url}"
    )
    run = find_run_for_commit(workspace, args.clone_url, args.commit_sha)
    if not run:
        parser.error(f"no such run found.")

    status = run.get("attributes", {}).get("status")
    if status in ["applied", "planned_and_finished"]:
        log.info(
            "%s in workspace %s for commit %s has already been %s",
            run["id"],
            args.workspace,
            args.commit_sha[0:7],
            status,
        )
        return 0

    try:
        log.info(
            "apply run %s in workspace %s from status %s",
            run["id"],
            args.workspace,
            status,
        )
        _post(f"runs/{run['id']}/actions/apply", data={"comment": args.comment})
    except TFEError as e:
        log.error(
            "apply of run %s in workspace %s failed, %s", run["id"], args.workspace, e
        )
        return 1

    result, run = wait_until(
        workspace,
        ["applied"],
        args.clone_url,
        args.commit_sha,
        args.maximum_wait_time * 60,
    )

    if run:
        show_apply(run)

    return result
