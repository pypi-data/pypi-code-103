from flask import Blueprint, jsonify
from flasgger import swag_from
from utils.decorators import login_required, validate_request


default = Blueprint('default', __name__)


@default.route('/default/search', methods=['POST'])
@login_required
@validate_request({
    'search': {'type': 'string'},
})
@swag_from('./docs/search.yml')
def search():
    return jsonify([])
