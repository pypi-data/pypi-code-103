from typing import Tuple

from faker import Faker
from dv_mock_api.enums import ObjectProperty
from dv_mock_api.models.dv_request import DvRequest
from dv_mock_api.settings import MAPPING, ObjectType
from http import HTTPStatus
import time

fake = Faker()


class LineItem(DvRequest):
    def __init__(self, partner_id, advertiser_id, lineitem_id) -> None:
        self.partner_id = str(partner_id)
        self.advertiser_id = str(advertiser_id)
        self.lineitem_id = str(lineitem_id)

    def create_body(self):
        return {
            "name": f"Partner - {fake.name()} Inc.",
            "partnerId": self.partner_id,
            "advertiserId": self.advertiser_id,
            "displayName": f"Advertiser - {fake.name()} Inc.",
            "campaignId": "string",
            "insertionOrderId": "string",
            "lineItemId": self.lineitem_id,
            "lineItemType": "enum (LineItemType)",
            "entityStatus": "enum (EntityStatus)",
            "updateTime": "string",
            "partnerCosts": [
                "object (PartnerCost)"
            ],
            "flight": "object (LineItemFlight)",
            "budget": "object (LineItemBudget)",
            "pacing": "object (Pacing)",
            "frequencyCap": "object (FrequencyCap)",
            "partnerRevenueModel": "object (PartnerRevenueModel)",
            "conversionCounting": "object (ConversionCountingConfig)",
            "creativeIds": [
                "string"
            ],
            "bidStrategy": "object (BiddingStrategy)",
            "integrationDetails": "object (IntegrationDetails)",
            "inventorySourceIds": [
                "string"
            ],
            "targetingExpansion": "object (TargetingExpansionConfig)",
            "warningMessages": [
                "enum (LineItemWarningMessage)"
            ],
            "mobileApp": "object (MobileApp)"
        }

    def request(self, response_type: HTTPStatus) -> Tuple[dict, HTTPStatus]:
        partner_config = MAPPING.get(ObjectType.PARTNERS).get(self.partner_id)
        if not partner_config:
            return {"message": "No partner found"}, HTTPStatus.NOT_FOUND

        advertisers = partner_config.get(ObjectType.ADVERTISERS)
        if not advertisers:
            return {"message": "No advertisers found"}, HTTPStatus.NOT_FOUND

        advertiser_config = advertisers.get(self.advertiser_id)
        if not advertiser_config:
            return {"message": "No advertiser found"}, HTTPStatus.NOT_FOUND

        lineitems = advertiser_config.get(ObjectType.LINEITEMS)
        if not lineitems:
            return {"message": "No lineitems found"}, HTTPStatus.NOT_FOUND

        lineitem_config = lineitems.get(self.lineitem_id)
        if not lineitem_config:
            return {"message": "No lineitem found"}, HTTPStatus.NOT_FOUND

        lineitem_http_response = lineitem_config.get(response_type)

        timeout = lineitem_config.get(ObjectProperty.TIMEOUT)
        time.sleep(timeout)

        return self.create_body(), lineitem_http_response
