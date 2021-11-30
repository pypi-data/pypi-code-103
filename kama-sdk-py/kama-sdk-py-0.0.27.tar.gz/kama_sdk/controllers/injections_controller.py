from flask import Blueprint, jsonify

from kama_sdk.core.core import updates_man, job_client

controller = Blueprint('injections_controller', __name__)

BASE_PATH = '/api/injections'

@controller.route(f'{BASE_PATH}/check_newer')
def check_newer():
  new_available = not updates_man.is_using_latest_injection()
  return jsonify(data=new_available)


@controller.route(f'{BASE_PATH}/latest/preview')
def preview():
  bundle = updates_man.latest_injection_bundle()
  preview_data = updates_man.preview_injection(bundle)
  return jsonify(data=preview_data)


@controller.route(f'{BASE_PATH}/latest/apply', methods=['POST'])
def apply_latest_injection():
  bundle = updates_man.latest_injection_bundle()
  action_kod = 'sdk.action.apply_vendor_injections'
  job_id = job_client.enqueue_action(action_kod, {'injections': bundle})
  return jsonify(data=dict(job_id=job_id))
