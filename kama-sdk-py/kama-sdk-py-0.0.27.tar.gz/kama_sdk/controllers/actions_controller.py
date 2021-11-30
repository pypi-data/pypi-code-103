from typing import Optional

from flask import Blueprint, jsonify

from kama_sdk.controllers import ctrl_utils
from kama_sdk.core.core import job_client
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.ext.misc import run_predicates_action
from kama_sdk.model.action.ext.misc.run_predicate_action import PREDICATE_KEY
from kama_sdk.model.action.ext.misc.run_predicates_action import RunPredicateAction, RunPredicatesAction
from kama_sdk.model.base import mc
from kama_sdk.model.base.common import PREDICATES_KEY
from kama_sdk.model.base.mc import FULL_SEARCHABLE_KEY
from kama_sdk.model.predicate.predicate import Predicate
from kama_sdk.serializers import action_serializer

controller = Blueprint('actions', __name__)

BASE_PATH = '/api/actions'

@controller.route(f"{BASE_PATH}/type/simple")
def list_actions_in_type():
  models = Action.inflate_all(q={
    FULL_SEARCHABLE_KEY: True,
    **ctrl_utils.space_selector(False)
  })
  serialized = list(map(action_serializer.serialize_std, models))
  return dict(data=serialized)


@controller.route(f"{BASE_PATH}/type/system_check")
def list_predicates_as_actions():
  predicates = Predicate.inflate_all(q={
    FULL_SEARCHABLE_KEY: True,
    **ctrl_utils.space_selector(True, True)
  })
  actions = [synthesize_predicate_action(p.get_id()) for p in predicates]
  serialized = list(map(action_serializer.serialize_std, actions))
  return dict(data=serialized)


@controller.route(f"{BASE_PATH}/<_id>")
def get_action(_id: str):
  if action := find_or_synthesize_action(_id):
    serialized = action_serializer.serialize_std(action)
    return jsonify(data=serialized)
  else:
    return jsonify(error=f"action not found for id='{_id}'"), 404


@controller.route(f"{BASE_PATH}/<_id>/run", methods=['POST'])
def run_action(_id: str):
  if action := find_or_synthesize_action(_id):
    job_id = job_client.enqueue_action(action.serialize())
    return jsonify(status='running', job_id=job_id)
  else:
    return jsonify(error=f"test not found for id='{_id}'"), 404


@controller.route(f"{BASE_PATH}/run_predicates", methods=['POST'])
def run_predicates():
  predicate_kods = ctrl_utils.parse_json_body().get('predicates')

  action = RunPredicatesAction.inflate({
    PREDICATES_KEY: predicate_kods
  })

  action_kod = action.serialize()
  job_id = job_client.enqueue_action(action_kod)
  return jsonify(status='running', job_id=job_id)


def find_or_synthesize_action(some_id: str) -> Optional[Action]:
  if action := find_action(some_id):
    return action
  else:
    return synthesize_predicate_action(some_id)


def find_action(action_id: str) -> Optional[Action]:
  if kod := ctrl_utils.id_param_to_kod(action_id):
    query = ctrl_utils.space_selector(False)
    return Action.inflate(kod, q=query, safely=True)
  else:
    return None


def synthesize_predicate_action(pred_id: str) -> Optional[Action]:
  return RunPredicateAction.inflate({
    mc.SPACE_KEY: ctrl_utils.space_id(True, True),
    PREDICATE_KEY: pred_id
  })
