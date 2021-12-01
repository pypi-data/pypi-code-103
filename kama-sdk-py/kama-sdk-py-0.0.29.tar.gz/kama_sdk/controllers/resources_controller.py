from typing import Union, Dict

from flask import Blueprint, jsonify
from k8kat.utils.main.api_defs_man import api_defs_man

from kama_sdk.controllers.ctrl_utils import parse_json_body
from kama_sdk.core.core.types import UserResQuery
from kama_sdk.model.k8s.variable_category import ResourceCategory
from kama_sdk.model.view import resources_table_helper as helper
from kama_sdk.serializers import resource_serializers as serializers

controller = Blueprint('resources', __name__)

BASE_PATH = '/api/resources'


@controller.route(f"{BASE_PATH}/columns", methods=['POST'])
def list_available_columns_ids():
  user_query = parse_args_query()
  if isinstance(user_query, Dict):
    res_kinds = user_query['resource_kinds']
    col_specs = helper.kinds2sorted_col_specs(res_kinds)
    serialized = list(map(serializers.ser_col_spec, col_specs))
    return jsonify(data=serialized)
  else:
    return jsonify({"error": user_query}), 400


@controller.route(f"{BASE_PATH}/definitions")
def list_definitions():
  data = api_defs_man.defs_list()
  return jsonify(data=data)


@controller.route(f"{BASE_PATH}/categories")
def list_categories():
  models = ResourceCategory.inflate_all()
  serialized = list(map(serializers.ser_category, models))
  return jsonify(data=serialized)


@controller.route(f"{BASE_PATH}/query", methods=['POST'])
def index():
  user_query = parse_args_query()
  if isinstance(user_query, Dict):
    kat_resources = helper.query_resources(user_query)
    frames = helper.compute_frames(user_query, kat_resources)
    return jsonify(data=frames)
  else:
    return jsonify({"error": user_query}), 400


def parse_args_query() -> Union[UserResQuery, str]:
  args = parse_json_body()
  raw_kinds = args.get("resource_kinds")
  col_ids = args.get("col_ids")
  problem_level = args.get("problem_level")
  max_cols = int(args.get("max_cols", 0))

  if problem_level not in ["error", "warning"]:
    problem_level = None

  kinds_with_nulls = list(map(api_defs_man.kind2plurname, raw_kinds))
  resource_kinds = [kind for kind in kinds_with_nulls if kind]

  return UserResQuery(
    resource_kinds=resource_kinds,
    problem_level=problem_level,
    col_ids=col_ids,
    max_cols=max_cols
  )
