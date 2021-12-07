from dv_mock_api.settings import MAPPING, ObjectType


def get_advertiser_to_partner_mapping() -> dict:
    advertisers = {}
    for partner_id, partner in MAPPING.get(ObjectType.PARTNERS).items():
        for advertiser_id in partner.get(ObjectType.ADVERTISERS).keys():
            advertisers[advertiser_id] = partner_id
    return advertisers


ADVERTISER_TO_PARTNER_KEYS = get_advertiser_to_partner_mapping()
