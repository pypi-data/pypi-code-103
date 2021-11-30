from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify, session
from flasgger import swag_from
from mongoCon import MongoCon
from utils.recycle import Recycle
from utils.responses import success_ok
from utils.decorators import login_required, validate_request
from datetime import datetime

ite = Blueprint('item', __name__)


@ite.route('/item/add', methods=['POST'])
@login_required
@validate_request({
    'name': {'type': 'string'},
})
@swag_from('./docs/add.yml')
def add_item():
    user = session.get('user_name', 'System')
    nitem = {
        "name": request.json['name'].strip(),
        "events": [
            {
                "event": "created",
                "user": user,
                "datetime": datetime.now(),
                "msg": "The user %s has created this registry." % user
            },
        ]
    }
    with MongoCon() as cnx:
        cnx.item.insert_one(nitem)
    return jsonify(nitem)


@ite.route('/item/get_all_items', methods=['GET'])
@login_required
@swag_from('./docs/get_all_items.yml')
def get_all_items():
    result = []
    with MongoCon() as cnx:
        result = list(cnx.item.find({}))
    return jsonify(result)


@ite.route('/item/delete_by_id', methods=['POST'])
@login_required
@validate_request({
    'ids': {'type': 'list'},
})
@swag_from('./docs/delete_by_id.yml')
def del_item():
    if request.json['ids']:
        Recycle.add('item', {"_id": {"$in": [ObjectId(_id) for _id in request.json['ids']]}}, "Name => {name}")
    return success_ok()
