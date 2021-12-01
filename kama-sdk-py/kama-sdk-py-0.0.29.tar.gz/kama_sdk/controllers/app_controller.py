from flask import Blueprint, jsonify

from kama_sdk.controllers import ctrl_utils
from kama_sdk.controllers.ctrl_utils import parse_json_body
from kama_sdk.core.core import job_client, presets_man, status_manager, consts
from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.core.types import KoD
from kama_sdk.model.action.ext.misc.run_predicates_action import RunPredicatesAction
from kama_sdk.model.base.common import PREDICATES_KEY
from kama_sdk.model.base.mc import ID_KEY, TITLE_KEY, INFO_KEY, LABELS_KEY
from kama_sdk.model.k8s.resource_group import ResourceGroup
from kama_sdk.model.predicate.multi_predicate import MultiPredicate
from kama_sdk.serializers.misc_sers import ser_victim_group

controller = Blueprint('app_controller', __name__)

BASE_PATH = '/api/app'


@controller.route(f'{BASE_PATH}/presets', methods=['GET', 'POST'])
def list_presets():
  space = ctrl_utils.space_id(True, True)
  serialized_presets = presets_man.load_all(space)
  return jsonify(data=serialized_presets)


@controller.route(f'{BASE_PATH}/presets/<_id>/commit-apply', methods=['POST'])
def commit_apply_preset(_id: str):
  space = ctrl_utils.space_id(True, True)
  if whitelist := parse_json_body().get('whitelist'):
    job_id = presets_man.load_and_start_apply_job(_id, space, whitelist)
    return jsonify(job_id=job_id)
  else:
    return jsonify(error='whitelist empty/absent'), 400


@controller.route(f'{BASE_PATH}/run-installation-preflight', methods=['POST'])
def run_global_preflight():
  action_kod = generate_preflight_action()
  job_id = job_client.enqueue_action(action_kod)
  return jsonify(data={'job_id': job_id})


@controller.route(f'{BASE_PATH}/compute-and-sync-statuses', methods=['POST'])
def compute_and_sync_status():
  statuses = status_manager.full_sync()
  return jsonify(statuses=statuses)


@controller.route(f'{BASE_PATH}/sync-status-hub', methods=['POST'])
def sync_status_hub():
  outcomes = status_manager.upload_all_statuses()
  return jsonify(success=outcomes.get('app'))


@controller.route(f'{BASE_PATH}/status', methods=['GET'])
def get_status():
  status = status_manager.compute_space_status(consts.APP_SPACE_ID)
  config_man.write_status(status)
  status_manager.upload_status(space=consts.APP_SPACE_ID)
  return jsonify(status=status)


@controller.route(f'{BASE_PATH}/uninstall-victim-groups')
def uninstall_victims():
  query = {LABELS_KEY: {'victim': True}}
  victim_groups = ResourceGroup.inflate_all(q=query)
  serialized = list(map(ser_victim_group, victim_groups))
  return jsonify(data=serialized)


@controller.route(f'{BASE_PATH}/deletion_selectors')
def deletion_selectors():
  deletion_map = 3
  return jsonify(data=deletion_map)


@controller.route(f'{BASE_PATH}/jobs/<job_id>/status')
def job_progress(job_id):
  status_wrapper = job_client.job_status(job_id)
  return jsonify(
    data=dict(
      status=status_wrapper.get_status(),
      progress=status_wrapper.get_progress_bundle(),
      result=status_wrapper.get_result()
    )
  )


def generate_preflight_action() -> KoD:
  query = {"space": consts.APP_SPACE_ID, "labels": {"preflight": True}}
  multi = MultiPredicate.inflate({
    ID_KEY: "sdk.predicate.preflight",
    TITLE_KEY: "Pre-Installation Preflight Checks",
    INFO_KEY: "Preempt incompatibilities and problems",
    PREDICATES_KEY: query
  })
  return RunPredicatesAction.from_predicate_subclass(multi)
