from flask import request, make_response, Blueprint
from flask_socketio import emit
from flasgger import swag_from
from utils.decorators import login_required
from utils.responses import success_ok
from const import APPLICATION_CODE
from dgapi import DGAPI


auth = Blueprint('authentication', __name__)


@auth.route('/one_authentication', methods=['GET'])
@swag_from('./docs/one_authentication.yml')
def one_authentication():
    res = DGAPI.post("one_authentication", {"application_code": APPLICATION_CODE}, {"content-type": "application/json"})
    return make_response(res.text, res.status_code)


@auth.route('/force_app_update', methods=['POST'])
@login_required
def force_app_update():
    emit("OnForceUpdate", request.json, broadcast=True, namespace="/")
    return success_ok()


@auth.route('/logout', methods=['GET'])
@login_required
@swag_from('./docs/logout.yml')
def logout():
    res = DGAPI.get("logout")
    return make_response(res.text, res.status_code)


@auth.route('/is_authorized', methods=['GET'])
@login_required
@swag_from('./docs/is_authorized.yml')
def is_authorized():
    return success_ok()
