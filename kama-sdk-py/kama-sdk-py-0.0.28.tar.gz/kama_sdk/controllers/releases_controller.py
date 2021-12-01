from flask import Blueprint, jsonify

from kama_sdk.controllers import ctrl_utils
from kama_sdk.core.core import job_client, updates_man
from kama_sdk.core.core.plugins_manager import plugins_manager
from kama_sdk.model.action.ext.update.fetch_release_action import RELEASE_ID_KEY
from kama_sdk.model.base.mc import SPACE_KEY

controller = Blueprint('releases_controller', __name__)

BASE_PATH = '/api/releases'


@controller.route(BASE_PATH)
def get_all_releases():
  spaces = ctrl_utils.space_id(False, False)
  if not spaces:
    spaces = ['app', *plugins_manager.get_registered_plugin_ids()]
  releases = updates_man.fetch_releases(spaces)
  return jsonify(data=releases or [])


@controller.route(f'{BASE_PATH}/next-available')
def fetch_next_available():
  update_or_none = updates_man.next_available()
  return jsonify(data=update_or_none)


@controller.route(f'{BASE_PATH}/<release_id>')
def show_update(release_id):
  space = ctrl_utils.space_id(True, True)
  if update := updates_man.fetch_release(release_id, space):
    return jsonify(data=update)
  else:
    return jsonify(error='release does not exist'), 400


@controller.route(f'{BASE_PATH}/<release_id>/preview-variables')
def preview_variables(release_id):
  space = ctrl_utils.space_id(True, True)
  if release := updates_man.fetch_release(release_id, space):
    variables = updates_man.preview_variables(release, space)
    return jsonify(data=variables)
  else:
    return jsonify(error='release does not exist'), 400


@controller.route(f'{BASE_PATH}/<release_id>/preview-manifest')
def preview_manifest(release_id):
  space = ctrl_utils.space_id(True, True)
  if release := updates_man.fetch_release(release_id, space):
    preview_bundle = updates_man.preview_manifest(release, space)
    return jsonify(data=preview_bundle)
  else:
    return jsonify(error='release does not exist'), 400


@controller.route(f'{BASE_PATH}/<release_id>/apply', methods=['POST'])
def install_update(release_id):
  patch = {
    RELEASE_ID_KEY: release_id,
    SPACE_KEY: ctrl_utils.space_id(True, True)
  }
  job_id = job_client.enqueue_action(apply_action_id, patch)
  return jsonify(data={'job_id': job_id})


apply_action_id = 'sdk.action.perform_update'