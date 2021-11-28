from typing import List

import requests

from foreverbull_core.models import service

from .exceptions import RequestError


class Service:
    def __init__(self, host: str, session: requests.session = None) -> None:
        self.host = host
        if session is None:
            session = requests.Session()
        self.session = session

    def list(self) -> List[service.Service]:
        rsp = self.session.get(f"http://{self.host}/api/v1/services")
        if not rsp.ok:
            raise RequestError(f"get call /services gave bad return code: {rsp.status_code}")
        return [service.Service(**s) for s in rsp.json()]

    def create(self, service: service.Service) -> service.Service:
        rsp = self.session.post(f"http://{self.host}/api/v1/services", json=service.dict())
        if not rsp.ok:
            raise RequestError(f"post call /services gave bad return code: {rsp.status_code}")
        return service.update_fields(rsp.json())

    def get(self, service_id: str) -> service.Service:
        rsp = self.session.get(f"http://{self.host}/api/v1/services/{service_id}")
        if not rsp.ok:
            raise RequestError(f"get call /services/{service_id} gave bad return code: {rsp.status_code}")
        return service.Service(**rsp.json())

    def update(self, service_id: str, service: service.Service) -> service.Service:
        rsp = self.session.put(f"http://{self.host}/api/v1/services/{service_id}", json=service.dict())
        if not rsp.ok:
            raise RequestError(f"put call /services/{service_id} gave bad return code: {rsp.status_code}")
        return service.update_fields(rsp.json())

    def delete(self, service_id: str) -> None:
        rsp = self.session.delete(f"http://{self.host}/api/v1/services/{service_id}")
        if not rsp.ok:
            raise RequestError(f"delete call /services/{service_id} gave bad return code: {rsp.status_code}")
        return None

    def list_instances(self, service_id: str) -> List[service.Instance]:
        rsp = self.session.get(f"http://{self.host}/api/v1/services/{service_id}/instances")
        if not rsp.ok:
            raise RequestError(f"get call /services/{service_id}/instances gave bad return code: {rsp.status_code}")
        return [service.Instance(**i) for i in rsp.json()]

    def get_instance(self, service_id: str, instance_id: str) -> service.Instance:
        rsp = self.session.get(f"http://{self.host}/api/v1/services/{service_id}/instances/{instance_id}")
        if not rsp.ok:
            raise RequestError(
                f"get call /services/{service_id}/instances/{instance_id} gave bad return code: {rsp.status_code}"
            )
        return service.Instance(**rsp.json())

    def update_instance(self, ins: service.Instance) -> service.Instance:
        rsp = self.session.patch(
            f"http://{self.host}/api/v1/services/{ins.service_id}/instances/{ins.instance_id}",
            params={"host": ins.host, "port": ins.port, "online": ins.online, "listen": ins.online},
        )
        if not rsp.ok:
            code = rsp.status_code  # to mitigate next line too long
            raise RequestError(
                f"get call /services/{ins.service_id}/instances/{ins.instance_id} gave bad return code: {code}"
            )
        return ins.update_fields(rsp.json())

    def delete_instance(self, service_id: str, instance_id: str) -> None:
        rsp = self.session.delete(f"http://{self.host}/api/v1/services/{service_id}/instances/{instance_id}")
        if not rsp.ok:
            raise RequestError(
                f"delete call /services/{service_id}/instances/{instance_id} gave bad return code: {rsp.status_code}"
            )
        return None
