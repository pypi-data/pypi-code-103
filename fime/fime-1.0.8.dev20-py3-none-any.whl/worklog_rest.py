import os
import sys
import traceback
from concurrent.futures import Future
from datetime import date, datetime, timedelta, time
from functools import partial
from textwrap import dedent
from threading import Lock
from typing import List, Dict, Tuple

import requests
from requests_futures.sessions import FuturesSession

from fime.config import Config
from fime.exceptions import FimeException
from fime.util import Status


class WorklogRest:
    def __init__(self, config: Config):
        self.config = config
        self.user_url = os.path.join(config.jira_url, "rest/api/2/myself")
        self.issue_url = os.path.join(config.jira_url, "rest/api/2/issue/{}")
        self.worklog_url = os.path.join(config.jira_url, "rest/api/2/issue/{}/worklog")
        self.worklog_update_url = os.path.join(config.jira_url, "rest/api/2/issue/{issue_key}/worklog/{worklog_id}")
        self.session = FuturesSession()
        self._user = None
        self._issue_state: Dict[str, Tuple[Status, str]] = dict()
        self._issue_state_lock = Lock()
        self._req_user()

    def _req_user(self):
        future = self.session.get(
            self.user_url,
            headers={
                "Authorization": f"Bearer {self.config.jira_token}",
                "Accept": "application/json",
            },
        )
        future.add_done_callback(self._resp_user)

    def _resp_user(self, future):
        try:
            self._user = future.result().json()["key"]
        except Exception:
            print("Could not get user key:\n", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)

    def get_issues_state(self, issue_keys: List[str]):
        ret = []
        with self._issue_state_lock:
            for issue_key in issue_keys:
                if issue_key not in self._issue_state:
                    self._issue_state[issue_key] = (Status.PROGRESS, "Working")
                    self._req_issue(issue_key)
                ret.append(self._issue_state[issue_key])
        return ret

    def purge_cache(self):
        self._issue_state = dict()

    def _req_issue(self, issue_key: str):
        future = self.session.get(
            self.issue_url.format(issue_key),
            headers={
                "Authorization": f"Bearer {self.config.jira_token}",
                "Accept": "application/json",
            },
        )
        future.add_done_callback(partial(self._resp_issue, issue_key))

    def _resp_issue(self, issue_key: str, future: Future):
        resp: requests.Response = future.result()
        with self._issue_state_lock:
            if resp.status_code == 200:
                hint = f'{issue_key} {resp.json()["fields"]["summary"]}'
                self._issue_state[issue_key] = (Status.OK, hint)
            else:
                self._issue_state[issue_key] = (Status.ERROR, "Could not find specified issue")

    def _upload_sanity_check(self, issue_keys: List[str]):
        if not self._user:
            raise FimeException("Could not get user key")
        for issue_key in issue_keys:
            if issue_key not in self._issue_state or self._issue_state[issue_key] is not Status.OK:
                raise FimeException(f"Issue with key {issue_key} in unexpected state")

    def upload(self, issues: List[Tuple[str, str, timedelta]], pdate: date):
        """@:param issues: [(
            "ISS-1234",
            "I did some stuff",
            timedelta(seconds=300),
        ), ... ]
        """
        self._upload_sanity_check(list(map(lambda x: x[0], issues)))
        for issue in issues:
            future = self.session.get(
                self.worklog_url.format(issue[0]),
                headers={
                    "Authorization": f"Bearer {self.config.jira_token}",
                    "Accept": "application/json",
                }
            )
            future.add_done_callback(partial(self._worklog_check_resp, issue[0], issue[1], issue[2], pdate))
            self._issue_state[issue[0]] = (Status.PROGRESS, "Working")

    def _worklog_check_resp(self, issue_key: str, comment: str, time_spent: timedelta, pdate: date, future: Future):
        resp = future.result()
        worklogs = resp.json()["worklogs"]
        worklog_id = None
        for log in worklogs:
            if log["author"]["key"] == self._user \
                    and datetime.strptime(log["started"], "%Y-%m-%dT%H:%M:%S.%f%z").date() == pdate:
                worklog_id = log["id"]
                break
        if worklog_id:
            print(f"Found existing worklog for issue {issue_key} with id {worklog_id}")
            self._worklog_update(issue_key, worklog_id, comment, time_spent, pdate)
        else:
            print(f"Did not find existing worklog for issue {issue_key}")
            self._worklog_create(issue_key, comment, time_spent, pdate)

    def _worklog_create(self, issue_key: str, comment: str, time_spent: timedelta, pdate: date):
        future = self.session.post(
            self.worklog_url.format(issue_key),
            headers={
                "Authorization": f"Bearer {self.config.jira_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={
                "started": datetime.combine(
                    pdate, time(8, 0), datetime.now().astimezone().tzinfo).strftime("%Y-%m-%dT%H:%M:%S.000%z"),
                "timeSpentSeconds": time_spent.seconds,
                "comment": comment,
            }
        )
        future.add_done_callback(partial(self._worklog_resp, issue_key))

    def _worklog_update(self, issue_key: str, worklog_id: str, comment: str, time_spent: timedelta, pdate: date):
        future = self.session.put(
            self.worklog_update_url.format(issue_key=issue_key, worklog_id=worklog_id),
            headers={
                "Authorization": f"Bearer {self.config.jira_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={
                "started": datetime.combine(
                    pdate, time(8, 0), datetime.now().astimezone().tzinfo).strftime("%Y-%m-%dT%H:%M:%S.000%z"),
                "timeSpentSeconds": time_spent.seconds,
                "comment": comment,
            }
        )
        future.add_done_callback(partial(self._worklog_resp, issue_key))

    def _worklog_resp(self, issue_key: str, future: Future):
        resp: requests.Response = future.result()
        with self._issue_state_lock:
            if resp.status_code == 200:
                self._issue_state[issue_key] = (Status.OK, "Successfully uploaded")
                print(f"Successfully uploaded issue {issue_key}")
            else:
                msg = dedent(f"""\
                    Worklog upload failed:
                    Method: {resp.request.method}
                    URL: {resp.request.url}
                    Response code: {resp.status_code}
                    Response: {resp.text}
                    """)
                self._issue_state[issue_key] = (Status.ERROR, msg)
                print(msg, file=sys.stderr)
