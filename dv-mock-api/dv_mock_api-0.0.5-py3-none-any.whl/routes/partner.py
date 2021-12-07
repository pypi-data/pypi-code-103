from http import HTTPStatus
from dv_mock_api.models.partner import Partner
from dv_mock_api.settings import MAPPING, ObjectType
from flask import Blueprint

partner_blueprint = Blueprint('partner', __name__,)


@partner_blueprint.route("/v1/partners/<partner_id>", methods=['PATCH'])
def patch_partner(partner_id):
    return Partner(partner_id=partner_id).patch()


@partner_blueprint.route("/v1/partners/<partner_id>", methods=['GET'])
def get_partner(partner_id):
    return Partner(partner_id=partner_id).get()


@partner_blueprint.route("/v1/partners", methods=['GET'])
def list_partner():
    partners = [Partner(partner_id=partner_id).get()
                for partner_id in MAPPING.get(ObjectType.PARTNERS).keys()]
    ok_partners = [partner for partner,
                   status_code in partners if status_code == HTTPStatus.OK]
    return {
        "partners": ok_partners,
    }, HTTPStatus.OK
