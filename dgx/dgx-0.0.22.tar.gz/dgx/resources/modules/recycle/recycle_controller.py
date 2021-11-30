from collections import defaultdict
from flask import Blueprint, jsonify, request, session
from flasgger import swag_from
from mongoCon import MongoCon
from pymongo import DESCENDING
from utils.decorators import login_required, validate_request, activity_log_decorator
from utils.recycle import Recycle
from utils.responses import success_ok
from re import compile, IGNORECASE
from bson import ObjectId


recycle = Blueprint('recycle', __name__)


def __create_query() -> dict:
    """
    Inicializa query con validacion de dealer_code y group_code si estos estan disponibles
    """
    query = defaultdict(list)
    session.get('group', False) and query["$and"].append({"group_code": session['group']})
    session.get('dealer', False) and query["$and"].append({"dealer_code": session['dealer']})
    return query


@recycle.route('/recycle/search', methods=['GET', 'POST'])
@login_required
@validate_request({
    'search': {'type': 'string'},
})
@swag_from('./docs/search.yml', methods=['GET'])
@swag_from('./docs/search.post.yml', methods=['POST'])
def get_recycle():
    result = []
    query = __create_query()
    with MongoCon() as cnx:
        if request.method == "GET":
            result = list(cnx.recycle.find(query)).sort("delete_date", DESCENDING)
        else:
            limit = request.json.get('limit', 25)
            skip = (request.json.get('page', 1) - 1) * limit
            request.json.get('type', False) and query["$and"].append({"type": request.json['type']})
            request.json.get('search', False) and query["$and"].append({"display": compile(request.json['search'].strip(), IGNORECASE)})
            result = list(cnx.recycle.find(query, {"events": False, "item": False}).skip(skip).limit(limit).sort("delete_date", DESCENDING))
    return jsonify(result)


@recycle.route('/recycle/get_by_id', methods=['POST'])
@login_required
@validate_request({
    '_id': {'type': 'object_id'},
})
@swag_from('./docs/get_by_id.yml')
def get_by_id():
    result = None
    with MongoCon() as cnx:
        result = cnx.recycle.find_one({"_id": ObjectId(request.json["_id"])})
    return jsonify(result)


@recycle.route('/recycle/recover_all', methods=['GET'])
@login_required
@activity_log_decorator('Recover all items')
@swag_from('./docs/recover_all.yml')
def recover_all():
    Recycle.recovery(__create_query())  # recupera todos los items
    return success_ok()


@recycle.route('/recycle/recover_by_id', methods=['POST'])
@login_required
@validate_request({
    'ids': {'type': 'list'}
})
@activity_log_decorator('Recover item')
@swag_from('./docs/recover_by_id.yml')
def recover_by_id():
    Recycle.recovery({"_id": {"$in": [ObjectId(_id) for _id in request.json["ids"]]}})
    return success_ok()


@recycle.route('/recycle/delete_all', methods=['DELETE'])
@login_required
@activity_log_decorator('Delete all items in recycle')
@swag_from('./docs/delete_all.yml')
def delete_all_recycle():
    with MongoCon() as cnx:
        cnx.recycle.delete_many(__create_query())  # eimina todos los registros permanentemente
    return success_ok()


@recycle.route('/recycle/delete_by_id', methods=['POST'])
@login_required
@validate_request({
    'ids': {'type': 'list'}
})
@activity_log_decorator('Delete all items in recycle')
@swag_from('./docs/delete_by_id.yml')
def delete_by_id():
    with MongoCon() as cnx:
        cnx.recycle.delete_many({"_id": {"$in": [ObjectId(_id) for _id in request.json["ids"]]}})  # eimina todos los registros permanentemente
    return success_ok()
