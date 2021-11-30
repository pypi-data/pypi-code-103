from typing import List, Dict, Any

from flask import Blueprint, jsonify, request

from kama_sdk.controllers import ctrl_utils
from kama_sdk.controllers.ctrl_utils import parse_json_body
from kama_sdk.core.core import job_client
from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.ktea.ktea_provider import ktea_client
from kama_sdk.model.action.base import action
from kama_sdk.model.action.base.action import TELEM_EVENT_TYPE_KEY
from kama_sdk.model.action.ext.misc import run_predicates_action
from kama_sdk.model.action.ext.misc.run_predicates_action import RunPredicatesAction
from kama_sdk.model.base import mc
from kama_sdk.model.base.mc import CONFIG_SPACE_KEY
from kama_sdk.model.supplier.base.misc_suppliers import VICTIM_KEYS_KEY
from kama_sdk.model.variable.manifest_variable import ManifestVariable
from kama_sdk.model.variable.variable_category import VariableCategory
from kama_sdk.serializers import variables_ser
from kama_sdk.utils import utils

BASE = '/api/variables'
DETAIL = f'{BASE}/detail/<variable_id>'

controller = Blueprint('variables_controller', __name__)
no_cat = "uncategorized"
ALL_CATS = 'all_categories'


@controller.route(f"{BASE}/categories")
def get_categories():
  categories: List[VariableCategory] = VariableCategory.inflate_all()
  serialized = list(map(variables_ser.serialize_category, categories))
  return jsonify(data=serialized)


@controller.route(f"{BASE}/health")
def get_correctness():
  output = []
  for variable in query_models():
    output.append({
      'config_space': variable.get_space_id(),
      'id': variable.get_flat_key(),
      'health': {
        'has_problems': variable.has_problems(),
        'is_read_blocked': variable.is_read_blocked()
      }
    })
  return jsonify(data=output)


@controller.route(f"{BASE}/all")
def get_all():
  variable_models = query_models()
  serialize = lambda v: variables_ser.standard(v, reload=False)
  serialized = list(map(serialize, variable_models))
  return jsonify(data=serialized)


def query_models() -> List[ManifestVariable]:
  config_man.invalidate_cmap()

  id_in_raw = request.args.get('id_in')
  id_in = id_in_raw.split(",") if id_in_raw else None
  category_eq = sanitize_cat(request.args.get('category'))

  category_filter = {'category': category_eq} if category_eq else {}
  id_filter = {mc.ID_KEY: id_in} if id_in else {}

  variable_models = ManifestVariable.inflate_all(q={
    **ctrl_utils.space_selector(False),
    **category_filter,
    **id_filter
  })

  is_pure = lambda mv: "template" not in mv.get_id()
  return [m for m in variable_models if is_pure(m)]


def sanitize_cat(raw_cat: Any) -> List[str]:
  if raw_cat:
    try:
      return str(raw_cat).split(',')
    except:
      return []
  else:
    return []


@controller.route(f"{BASE}/defaults")
def manifest_variables_defaults():
  as_dict = config_man.get_default_vars()
  return jsonify(data=as_dict)


@controller.route(f'{BASE}/populate-defaults')
def populate_defaults():
  space = ctrl_utils.space_id(True, True)
  defaults = ktea_client(space=space).load_default_values()
  config_man.write_default_vars(defaults, space=space)
  config_man.invalidate_cmap()
  return jsonify(data=defaults)


@controller.route(DETAIL)
def get_variable(variable_id):
  """
  Finds and serializes the chart variable.
  :param variable_id: key used to locate the right chart variable.
  :return: serialized chart variable.
  """
  space_id = ctrl_utils.space_id(True, True)
  _model = ManifestVariable.find_or_synthesize(variable_id, space_id)
  serialized = variables_ser.full(_model)
  return jsonify(data=serialized)


@controller.route(f'{DETAIL}/health_predicates/run', methods=['POST'])
def run_variable_predicates(variable_id):
  """
  Finds and serializes the chart variable.
  :param variable_id: key used to locate the right chart variable.
  :return: serialized chart variable.
  """
  space_id = ctrl_utils.space_id(True, True)
  _model = ManifestVariable.find_or_synthesize(variable_id, space_id)
  predicate_kods = [p.serialize() for p in _model.get_health_predicates()]
  action_kod = {
    mc.KIND_KEY: RunPredicatesAction.__name__,
    run_predicates_action.PREDICATES_KEY: predicate_kods
  }

  job_id = job_client.enqueue_action(action_kod)
  return jsonify(data={'job_id': job_id})


@controller.route(f'{BASE}/commit-apply', methods=['POST'])
def commit_and_apply_variable_assignments():
  """
  Updates the chart variable with new value.
  :return: status of the update.
  """
  params: Dict = parse_json_body()
  possibly_flat_assignments = params['assignments']
  assignments = utils.flat2deep(possibly_flat_assignments)

  job_id = job_client.enqueue_action(
    'sdk.action.commit_template_apply_safely',
    patch={
      "values": assignments,
      TELEM_EVENT_TYPE_KEY: action.SET_VAR_EVENT_TYPE,
      CONFIG_SPACE_KEY: ctrl_utils.space_id(True, True)
    }
  )

  return jsonify(data=dict(job_id=job_id))


@controller.route(f'{BASE}/commit-unsets', methods=['POST'])
def commit_and_unset_variable():
  """
  Updates the chart variable with new value.
  :return: status of the update.
  """
  params: Dict = parse_json_body()
  victim_keys = params['victim_keys']

  job_id = job_client.enqueue_action(
    'sdk.action.unset_template_apply_safely',
    patch={
      VICTIM_KEYS_KEY: victim_keys,
      TELEM_EVENT_TYPE_KEY: action.UNSET_VAR_EVENT_TYPE,
      CONFIG_SPACE_KEY: ctrl_utils.space_id(True, True)
    }
  )

  return jsonify(data=dict(job_id=job_id))


@controller.route(f'{DETAIL}/validate', methods=['POST'])
def validate_variable_value(variable_id):
  """
  Validates the chart variable against
  :param variable_id: key to locate the right chart variable.
  :return: validation status, with tone and message if unsuccessful.
  """
  space = ctrl_utils.space_id(True, True)
  value = parse_json_body()['value']
  variable_model = ManifestVariable.find_or_synthesize(variable_id, space)
  eval_result = variable_model.validate(value)
  status = 'valid' if eval_result['met'] else eval_result['tone']
  message = None if eval_result['met'] else eval_result['reason']
  return jsonify(data=dict(status=status, message=message))


space_id_key = 'space'
