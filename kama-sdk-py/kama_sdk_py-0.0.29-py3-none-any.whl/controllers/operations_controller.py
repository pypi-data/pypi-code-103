from typing import Dict, Optional, List

from flask import Blueprint, jsonify, request
from k8kat.auth.kube_broker import broker

from kama_sdk.controllers import ctrl_utils
from kama_sdk.controllers.ctrl_utils import parse_json_body
from kama_sdk.core.core import job_client
from kama_sdk.core.core.consts import TARGET_STANDARD
from kama_sdk.model.action.ext.misc.run_predicates_action import RunPredicatesAction
from kama_sdk.model.base.mc import FULL_SEARCHABLE_KEY
from kama_sdk.model.operation.operation import Operation
from kama_sdk.model.operation.operation_state import OperationState, operation_states
from kama_sdk.model.operation.step import Step
from kama_sdk.serializers import operation_serial as operation_serial, step_serial
from kama_sdk.utils import utils
from kama_sdk.utils.logging import lwar

OPERATIONS_PATH = '/api/operations'
OPERATION_PATH = f'/{OPERATIONS_PATH}/<operation_id>'

STEPS_PATH = f'{OPERATION_PATH}/steps'
STEP_PATH = f'{STEPS_PATH}/<step_id>'

FIELDS_PATH = f'{STEP_PATH}/fields'
FIELD_PATH = f'{FIELDS_PATH}/<field_id>'

controller = Blueprint('operations_controller', __name__)


@controller.route(OPERATIONS_PATH)
def operations_index():
  """
  Lists all existing Operations for a local app, except system ones.
  :return: list of minimally serialized Operation objects.
  """
  operations = Operation.inflate_all(q={FULL_SEARCHABLE_KEY: True})
  serialized = list(map(operation_serial.ser_standard, operations))
  return jsonify(data=serialized)


@controller.route(OPERATION_PATH)
def operations_show(operation_id):
  """
  Finds and returns a particular Operation using operation_id.
  :param operation_id: operation id to search by.
  :return: fully serialized Operation object.
  """
  if operation := find_operation(operation_id):
    return jsonify(data=operation_serial.ser_full(operation))
  else:
    return jsonify(error=f"no operation '{operation_id}'"), 404


@controller.route(f'{OPERATIONS_PATH}/osts')
def operations_ost_index():
  """
  Generates a list of currently available OperationStates.
  :return: list of currently available OperationStates.
  """
  return jsonify(data=operation_states)


@controller.route(f'{OPERATION_PATH}/generate-ost', methods=['POST'])
def operations_gen_ost(operation_id):
  """
  Generates a new OST (random 10 character string).
  :return: new OST.
  """
  uuid = OperationState.gen(operation_id)
  return jsonify(data=uuid)


@controller.route(f"{OPERATION_PATH}/eval-preflight", methods=['POST'])
def eval_preflight(operation_id):
  """
  Finds the Prerequisite with a matching operation_id and prerequisite_id,
  and evaluates it.
  :param operation_id: operation id to search by.
  :return: dict containing results of evaluation.
  """
  operation = find_operation(operation_id)
  if predicate := operation.generate_preflight_multi_predicate():
    action_config = RunPredicatesAction.from_predicate_subclass(predicate)
    job_id = job_client.enqueue_action(action_config)
    return jsonify(data=dict(job_id=job_id))
  else:
    return jsonify(data=dict(job_id=None))


@controller.route(f"{STEP_PATH}/refresh", methods=['POST'])
def step_refresh(operation_id, step_id):
  """
  Finds the Step with a matching operation_id and step_id.
  :param operation_id: operation id to search by.
  :param step_id: step id to search by.
  :return: serialized Step object.
  """
  values: Dict = utils.flat2deep(parse_json_body()['values'])
  op_state = find_op_state(operation_id=operation_id)
  step = find_step(operation_id, step_id)
  find_op_state().gen_step_state(step, keep=False)
  asgs = step.partition_vars(values, op_state)
  serialized = step_serial.ser_refreshed(step, values, op_state)
  return jsonify(data=dict(
    step=serialized,
    manifest_assignments=asgs.get(TARGET_STANDARD)
  ))


@controller.route(f"{STEP_PATH}/preview-chart-assignments", methods=['POST'])
def step_preview_chart_assigns(operation_id, step_id):
  """
  Returns the chart assignments that would be committed if the step were submitted
  with current user input.
  :param operation_id: operation id used to locate the right step
  :param step_id: step id used to locate the right step
  :return: dictionary with chart assigns.
  """
  values = utils.flat2deep(parse_json_body()['values'])
  op_state = find_op_state(operation_id=operation_id)
  step = find_step(operation_id, step_id)
  op_state.gen_step_state(step, keep=False)
  asgs = step.partition_vars(values, op_state)
  return jsonify(data=asgs[TARGET_STANDARD])


@controller.route(f"{STEP_PATH}/run", methods=['POST'])
def step_run(operation_id, step_id):
  """
  Submits a step. This includes:
    1. Finding the appropriate OperationState
    2. Appending a new StepState to OperationState
    3. Committing the step (See docs for step commit)
    4. Updating the StepState with the details of the commit outcome
  :param operation_id: operation id to search by.
  :param step_id: step id to search by.
  :return: dict containing submit status, message and logs.
  """
  values = utils.flat2deep(parse_json_body()['values'])
  step = find_step(operation_id, step_id)
  op_state = find_op_state(operation_id=operation_id)
  step_state = op_state.gen_step_state(step)
  job_id = step.run(values, step_state)
  return jsonify(data=dict(job_id=job_id))


@controller.route(f'{STEP_PATH}/next')
def steps_next_id(operation_id, step_id):
  """
  computes and returns the id of the next step.
  :param operation_id: operation id to locate the right step.
  :param step_id: step id to locate the right step.
  :return: computed id of next step or "done" if no more steps left.
  """
  operation = find_operation(operation_id)
  step = operation.find_step_by_id(step_id)
  op_state = find_op_state()
  result = operation.compute_next_step_id(step, op_state)
  return jsonify(step_id=result)


@controller.route(f'{FIELD_PATH}/validate', methods=['POST'])
def step_field_validate(operation_id, step_id, field_id):
  value = parse_json_body()['value']
  step = find_step(operation_id, step_id)
  op_state = find_op_state(operation_id=operation_id)
  eval_result = step.validate_field(field_id, value, op_state)
  status = 'valid' if eval_result['met'] else eval_result['tone']
  message = None if eval_result['met'] else eval_result['reason']
  return jsonify(data=dict(status=status, message=message))


def find_operation(operation_id: str) -> Optional[Operation]:
  """
  Inflates (instantiates) an instance of an Operation by operation_id.
  :param operation_id: desired operation to be inflated.
  :return: Operation instance.
  """
  if kod := ctrl_utils.id_param_to_kod(operation_id):
    return Operation.inflate(kod, safely=True)
  else:
    return None


def find_step(operation_id, step_id) -> Step:
  """
  Finds the Step with a matching operation_id and step_id.
  :param operation_id: operation id to search by.
  :param step_id: step id to search by.
  :return: Step class instance.
  """
  operation = find_operation(operation_id)
  return operation.find_step_by_id(step_id)


def extract_ost_id(try_sources: List[Dict]) -> Optional[str]:
  try_keys = ["ostId", "OstId", "Ostid", "ostid", "ost_id"]
  for source in try_sources:
    for key in try_keys:
      if value := source.get(key):
        return value
  return None


def find_op_state(**kwargs) -> OperationState:
  op_id = kwargs.get('operation_id')
  raise_on_fail = kwargs.get('raise_on_fail', False)

  ost_id = extract_ost_id([request.headers, request.args])
  op_state = OperationState.find(ost_id) if ost_id else None

  if not op_state:
    error_message = f"ost_id missing or invalid ({ost_id})"
    if broker.is_in_cluster_auth() and raise_on_fail:
      raise RuntimeError(error_message)
    uuid = OperationState.gen(op_id)
    op_state = OperationState.find(uuid)
    lwar(error_message)

  return op_state
