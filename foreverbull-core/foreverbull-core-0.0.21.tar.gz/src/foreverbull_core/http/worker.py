from typing import List

import requests

from foreverbull_core.http import RequestError
from foreverbull_core.models import worker


class Worker:
    def __init__(self, host, session=None) -> None:
        self.host = host
        if session is None:
            session = requests.Session()
        self.session = session

    def list(self) -> List[worker.Config]:
        rsp = self.session.get(f"http://{self.host}/api/v1/workers")
        if not rsp.ok:
            raise RequestError(f"get call /workers gave bad return code: {rsp.status_code}")
        return [worker.Config(**w) for w in rsp.json()]

    def create(self, worker: worker.Config) -> worker.Config:
        rsp = self.session.post(f"http://{self.host}/api/v1/workers", json=worker.json())
        if not rsp.ok:
            raise RequestError(f"post call /workers gave bad return code: {rsp.status_code}")
        return worker.update_fields(rsp.json())

    def get(self, worker_id: int) -> worker.Config:
        rsp = self.session.get(f"http://{self.host}/api/v1/workers/{worker_id}")
        if not rsp.ok:
            raise RequestError(f"get call /workers/{worker_id} gave bad return code: {rsp.status_code}")
        return worker.Config(**rsp.json())

    def update(self, worker_id: int, worker: worker.Config) -> worker.Config:
        rsp = self.session.put(f"http://{self.host}/api/v1/workers/{worker_id}", json=worker.json())
        if not rsp.ok:
            raise RequestError(f"put call /workers/{worker_id} gave bad return code: {rsp.status_code}")
        return worker.update_fields(rsp.json())

    def delete(self, worker_id: int) -> None:
        rsp = self.session.delete(f"http://{self.host}/api/v1/workers/{worker_id}")
        if not rsp.ok:
            raise RequestError(f"delete call /workers/{worker_id} gave bad return code: {rsp.status_code}")
        return None
