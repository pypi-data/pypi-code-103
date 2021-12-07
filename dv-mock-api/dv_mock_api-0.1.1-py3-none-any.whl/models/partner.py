from typing import Tuple

from faker import Faker

from dv_mock_api.enums import ObjectProperty
from dv_mock_api.models.dv_request import DvRequest
from dv_mock_api.settings import MAPPING, ObjectType
from http import HTTPStatus
import time

fake = Faker()


class Partner(DvRequest):
    def __init__(self, partner_id) -> None:
        self.partner_id = str(partner_id)

    def create_body(self) -> dict:
        return {
            "name": f"Partner - {fake.name()} Inc.",
            "partnerId": self.partner_id,
            "displayName": f"Advertiser - {fake.name()} Inc.",
        }

    def request(self, response_type: HTTPStatus) -> Tuple[dict, HTTPStatus]:
        partner_config = MAPPING.get(ObjectType.PARTNERS).get(self.partner_id)
        if not partner_config:
            return {"message": "No partner found"}, HTTPStatus.NOT_FOUND

        partner_http_response = partner_config.get(response_type)

        timeout = partner_config.get(ObjectProperty.TIMEOUT)
        time.sleep(timeout)

        return self.create_body(), partner_http_response
