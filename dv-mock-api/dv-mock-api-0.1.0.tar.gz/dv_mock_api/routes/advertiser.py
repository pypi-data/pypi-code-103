from http import HTTPStatus
from dv_mock_api.helpers.prefilter import ADVERTISER_TO_PARTNER_KEYS
from dv_mock_api.models.advertiser import Advertiser
from dv_mock_api.settings import MAPPING, ObjectType
from flask import Blueprint, request

advertiser_blueprint = Blueprint('advertiser', __name__, )


@advertiser_blueprint.route("/v1/advertisers/<advertiser_id>", methods=['PATCH'])
def patch_advertiser(advertiser_id):
    return Advertiser(
        partner_id=ADVERTISER_TO_PARTNER_KEYS.get(advertiser_id),
        advertiser_id=advertiser_id
    ).patch()


@advertiser_blueprint.route("/v1/advertisers/<advertiser_id>", methods=['GET'])
def get_advertiser(advertiser_id):
    return Advertiser(
        partner_id=ADVERTISER_TO_PARTNER_KEYS.get(advertiser_id),
        advertiser_id=advertiser_id
    ).get()


@advertiser_blueprint.route("/v1/advertisers", methods=['GET'])
def list_advertisers():
    partner_id = request.args.get("partnerId")
    if not partner_id:
        return {"message": "No parter id supplied."}, HTTPStatus.BAD_REQUEST

    advertisers = MAPPING.get(ObjectType.PARTNERS).get(
        partner_id
    ).get(ObjectType.ADVERTISERS)
    advertisers = [Advertiser(partner_id=partner_id, advertiser_id=advertiser_id).get(
    ) for advertiser_id in advertisers.keys()]
    advertisers = [advertiser for advertiser,
                   status_code in advertisers if status_code == HTTPStatus.OK]

    return {
        "advertisers": advertisers,
    }, HTTPStatus.OK
