from http import HTTPStatus
from dv_mock_api.models.lineitem import LineItem
from dv_mock_api.settings import MAPPING, ObjectType
from dv_mock_api.helpers.prefilter import ADVERTISER_TO_PARTNER_KEYS
from flask import Blueprint

lineitem_blueprint = Blueprint('lineitem', __name__,)


@lineitem_blueprint.route("/v1/advertisers/<advertiser_id>/lineItems/<lineitem_id>", methods=['PATCH'])
def patch_lineitem(advertiser_id, lineitem_id):
    return LineItem(
        partner_id=ADVERTISER_TO_PARTNER_KEYS.get(advertiser_id),
        advertiser_id=advertiser_id,
        lineitem_id=lineitem_id
    ).patch()


@lineitem_blueprint.route("/v1/advertisers/<advertiser_id>/lineItems/<lineitem_id>", methods=['GET'])
def get_lineitem(advertiser_id, lineitem_id):
    return LineItem(
        partner_id=ADVERTISER_TO_PARTNER_KEYS.get(advertiser_id),
        advertiser_id=advertiser_id,
        lineitem_id=lineitem_id
    ).get()


@lineitem_blueprint.route("/v1/advertisers/<advertiser_id>/lineItems", methods=['GET'])
def list_lineitems(advertiser_id):
    lineitem_objects = []
    partner_id = ADVERTISER_TO_PARTNER_KEYS.get(advertiser_id)
    partner = MAPPING.get(ObjectType.PARTNERS).get(partner_id)
    if not partner:
        return {
            "message": "Advertiser {advertiser_id} does not exist"
        }, HTTPStatus.BAD_REQUEST

    advertisers = partner.get(ObjectType.ADVERTISERS)
    advertiser_ids = advertisers.keys()

    lineitem_ids = []
    for advertiser_id in advertiser_ids:
        lineitem_ids = [
            *lineitem_ids, *advertisers.get(advertiser_id).get(ObjectType.LINEITEMS).keys()]

    for lineitem_id in lineitem_ids:
        lineitem_object, status_code = LineItem(
            partner_id=partner_id, advertiser_id=advertiser_id, lineitem_id=lineitem_id).get()
        if status_code == HTTPStatus.OK:
            lineitem_objects.append(lineitem_object)

    return {
        "lineItems": lineitem_objects,
        "nextPageToken": ""
    }, HTTPStatus.OK
