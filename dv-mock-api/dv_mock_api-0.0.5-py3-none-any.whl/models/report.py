from typing import Tuple
from faker import Faker
from httplib2 import Http
from dv_mock_api.enums import ObjectProperty
from dv_mock_api.models.dbm_request import DbmRequest
from dv_mock_api.settings import MAPPING, ObjectType
from http import HTTPStatus
from random import randint
import time

fake = Faker()


class Report(DbmRequest):
    def __init__(self, query_id=None, base_url="http://localhost:5050", create_query=False) -> None:
        self.base_url = base_url
        self.query_id = query_id if query_id else randint(1000, 9999)
        self.file_name = None
        self.create_query = create_query

    def create_body(self) -> dict:
        return {
            "kind": "doubleclickbidmanager#query",
            "queryId": self.query_id,
            "metadata": {
                "running": False,
                "googleCloudStoragePathForLatestReport": f"{self.base_url}/download/{self.query_id}.csv",
            }
        }

    def request(self, response_key: HTTPStatus, file=False) -> Tuple[dict, HTTPStatus]:
        if self.create_query:
            return self.create_body(), HTTPStatus.OK

        report_config = MAPPING.get(ObjectType.REPORTS).get(self.query_id)
        if not report_config:
            return {"message": "No report found"}, HTTPStatus.NOT_FOUND

        report_http_response = report_config.get(response_key)
        file_name = report_config.get(ObjectProperty.FILE)

        timeout = report_config.get(ObjectProperty.TIMEOUT)
        time.sleep(timeout)

        if file:
            self.file_name = file_name

        return self.create_body(), report_http_response
