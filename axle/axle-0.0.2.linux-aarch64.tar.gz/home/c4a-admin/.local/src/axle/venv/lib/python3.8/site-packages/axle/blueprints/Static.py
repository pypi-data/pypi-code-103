from flask import Blueprint, abort, current_app, send_from_directory

blueprint = Blueprint('static', __name__)

@blueprint.route('/<path:path>')
def get_static(path):
    return send_from_directory(current_app.static_folder, path)
