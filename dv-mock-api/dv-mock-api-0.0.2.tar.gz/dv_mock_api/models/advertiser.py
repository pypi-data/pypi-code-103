from typing import Tuple

from faker import Faker
from dv_mock_api.enums import ObjectProperty
from dv_mock_api.models.dv_request import DvRequest
from dv_mock_api.settings import MAPPING, ObjectType
from http import HTTPStatus
import time

fake = Faker()


class Advertiser(DvRequest):
    def __init__(self, partner_id, advertiser_id) -> None:
        self.partner_id = str(partner_id)
        self.advertiser_id = str(advertiser_id)

    def create_body(self):
        return {
            "name": f"Partner - {fake.name()} Inc.",
            "partnerId": self.partner_id,
            "advertiserId": self.advertiser_id,
            "displayName": f"Advertiser - {fake.name()} Inc.",
        }

    def request(self, response_type: HTTPStatus) -> Tuple[dict, HTTPStatus]:
        partner_config = MAPPING.get(ObjectType.PARTNERS).get(self.partner_id)
        if not partner_config:
            return {"message": "No partner found"}, HTTPStatus.NOT_FOUND

        advertiser_config = partner_config.get(
            ObjectType.ADVERTISERS).get(self.advertiser_id)
        if not advertiser_config:
            return {"message": "No partner found"}, HTTPStatus.NOT_FOUND

        advertiser_http_response = advertiser_config.get(response_type)

        timeout = advertiser_config.get(ObjectProperty.TIMEOUT)
        time.sleep(timeout)

        return self.create_body(), advertiser_http_response
