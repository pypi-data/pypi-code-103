import requests
from flask import Blueprint, request

discover_blueprint = Blueprint('discovery', __name__,)


@discover_blueprint.route("/discover/displayvideo/v1", methods=['GET'])
def get_dv360_discovery():
    base = request.base_url.replace("/discover/displayvideo/v1", "")
    discovery_document = requests.get(
        "https://displayvideo.googleapis.com/$discovery/rest?version=v1").json()
    discovery_document["rootUrl"] = f"{base}"
    return discovery_document


@discover_blueprint.route("/discover/doubleclickbidmanager/v1.1", methods=['GET'])
def get_dmb_discovery():
    base = request.base_url.replace("/discover/doubleclickbidmanager/v1.1", "")
    discovery_document = requests.get(
        "https://doubleclickbidmanager.googleapis.com/$discovery/rest?version=v1.1").json()
    discovery_document["rootUrl"] = f"{base}"
    return discovery_document
