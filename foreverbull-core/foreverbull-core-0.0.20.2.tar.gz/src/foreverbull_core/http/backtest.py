from typing import List

import requests

from foreverbull_core.http import RequestError
from foreverbull_core.models import backtest, service


class Backtest:
    def __init__(self, host, session=None) -> None:
        self.host = host
        if session is None:
            session = requests.Session()
        self.session = session

    def list(self) -> List[backtest.Config]:
        rsp = self.session.get(f"http://{self.host}/api/v1/backtests")
        if not rsp.ok:
            raise RequestError(f"get call /backtests gave bad return code: {rsp.status_code}")
        return [backtest.Config(**b) for b in rsp.json()]

    def create(self, backtest: backtest.Config) -> backtest.Config:
        rsp = self.session.post(f"http://{self.host}/api/v1/backtests", json=backtest.dict())
        if not rsp.ok:
            raise RequestError(f"post call /backtests gave bad return code: {rsp.status_code}")
        return backtest.update_fields(rsp.json())

    def get(self, backtest_id: str) -> backtest.Config:
        rsp = self.session.get(f"http://{self.host}/api/v1/backtests/{backtest_id}")
        if not rsp.ok:
            raise RequestError(f"get call /backtests/{backtest_id} gave bad return code: {rsp.status_code}")
        return backtest.Config(**rsp.json())

    def delete(self, backtest_id: str) -> None:
        rsp = self.session.delete(f"http://{self.host}/api/v1/backtests/{backtest_id}")
        if not rsp.ok:
            raise RequestError(f"delete call /backtests/{backtest_id} gave bad return code: {rsp.status_code}")
        return None

    def list_sessions(self, backtest_id: str) -> List[backtest.Session]:
        rsp = self.session.get(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions")
        if not rsp.ok:
            raise RequestError(f"get call /backtests/{backtest_id}/sessions gave bad return code: {rsp.status_code}")
        return [backtest.Session(**s) for s in rsp.json()]

    def create_session(self, backtest_id: str, session: backtest.Session) -> backtest.Session:
        rsp = self.session.post(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions", json=session.dict())
        if not rsp.ok:
            raise RequestError(f"post call /backtests/{backtest_id}/sessions gave bad return code: {rsp.status_code}")
        return session.update_fields(rsp.json())

    def get_session(self, backtest_id, session_id: str) -> backtest.Session:
        rsp = self.session.get(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions/{session_id}")
        if not rsp.ok:
            raise RequestError(
                f"get call /backtests/{backtest_id}/sessions/{session_id} gave bad return code: {rsp.status_code}"
            )
        return backtest.Session(**rsp.json())

    def delete_session(self, backtest_id: str, session_id: str) -> None:
        rsp = self.session.delete(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions/{session_id}")
        if not rsp.ok:
            raise RequestError(
                f"delete call /backtests/{backtest_id}/sessions/{session_id} gave bad return code: {rsp.status_code}"
            )
        return None

    def setup_session(self, backtest_id: str, session_id: str) -> None:
        rsp = self.session.post(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions/{session_id}/setup")
        if not rsp.ok:
            code = rsp.status_code  # to mitigate line too long
            raise RequestError(
                f"post call /backtests/{backtest_id}/sessions/{session_id}/setup gave bad return code: {code}"
            )
        return None

    def configure_session(self, backtest_id: str, session_id: str, raw_conn: service.RawConnection = None) -> None:
        rsp = self.session.post(
            f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions/{session_id}/configure", json=raw_conn.dict()
        )
        if not rsp.ok:
            code = rsp.status_code  # to mitigate line too long
            raise RequestError(
                f"post call /backtests/{backtest_id}/sessions/{session_id}/configure gave bad return code: {code}"
            )
        return None

    def run_session(self, backtest_id: str, session_id: str) -> None:
        rsp = self.session.post(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions/{session_id}/run")
        if not rsp.ok:
            raise RequestError(
                f"post call /backtests/{backtest_id}/sessions/{session_id}/run gave bad return code: {rsp.status_code}"
            )
        return None
