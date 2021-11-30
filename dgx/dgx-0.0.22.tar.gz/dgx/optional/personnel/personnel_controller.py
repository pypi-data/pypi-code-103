from flask import Blueprint, request, jsonify
from flasgger import swag_from
from utils.decorators import login_required, validate_request
from dgapi import DGAPI


psnl = Blueprint('personnel', __name__)


@psnl.route('/personnel/search', methods=['POST'])
@login_required
@validate_request({
    'search': {'type': 'string'},
})
@swag_from('./docs/search.yml')
def search():
    resp = DGAPI.post('get_personnel', request.json)
    return jsonify(resp.json())


@psnl.route('/personnel/get_by_id', methods=['POST'])
@login_required
@validate_request({
    'id': {'type': 'number'},
})
@swag_from('./docs/get_by_id.yml')
def get_by_id():
    resp = DGAPI.get('get_user_by_id/%s' % request.json.get("id"))
    if resp.status_code == 200:
        item = resp.json()
        del item['apps']
        return jsonify(item)
    return jsonify(None)


@psnl.route('/personnel/update', methods=['POST'])
@login_required
@validate_request({
    'id': {'type': 'number'},
})
@swag_from('./docs/update.yml')
def update():
    request.json.pop('apps', None)
    resp = DGAPI.post('update_user', request.json)
    return jsonify(resp.json())


@psnl.route('/personnel/get_roles', methods=['GET'])
@login_required
@swag_from('./docs/get_roles.yml')
def get_roles():
    resp = DGAPI.get('get_roles')
    return jsonify(resp.json())
