import base64
import json
from typing import Dict, Any, Type

from flask import Blueprint, jsonify, request

from kama_sdk.model.view.grid_view_spec import GridViewSpec
from kama_sdk.model.view.table_view_spec import TableViewSpec
from kama_sdk.model.view.view_group import ViewGroup
from kama_sdk.model.view.view_spec import ViewSpec
from kama_sdk.serializers.view_spec_ser import ser_group_meta
from kama_sdk.utils.logging import lwar

controller = Blueprint('view_specs_controller', __name__)

BASE_PATH = '/api/view_specs'


@controller.route(f"{BASE_PATH}/groups/<_group_id>")
def get_index(_group_id: str):
  group_id = "app.view-group.home" if _group_id == 'home' else _group_id
  if group := ViewGroup.inflate(group_id, safely=True):
    return jsonify(data=ser_group_meta(group))
  else:
    return jsonify({'error': 'no such view group'}), 404


@controller.route(f'{BASE_PATH}/containers/<spec_id>/meta')
def get_view_meta(spec_id):
  if page_spec := ViewSpec.inflate(spec_id, patch=compute_patch()):
    if is_descendant(page_spec, GridViewSpec, TableViewSpec):
      meta = page_spec.compute_spec()
      return jsonify(data=meta)
    else:
      return jsonify({'error': f"spec '{spec_id}' is not a grid"}), 400
  else:
    return jsonify({'error': f"no such '{spec_id}'"}), 400


@controller.route(f'{BASE_PATH}/tables/<spec_id>/compute')
def get_view_data(spec_id):
  if spec_model := ViewSpec.inflate(spec_id, patch=compute_patch()):
    if isinstance(spec_model, TableViewSpec):
      data = spec_model.compute_frame_view_specs()
      return jsonify(data=data)
    else:
      return jsonify({'error': f"spec '{spec_id}' is not a table"}), 400
  else:
    return jsonify({'error': f"no such spec '{spec_id}'"}), 400


@controller.route(f'{BASE_PATH}/grids/<grid_id>/cells/<cell_id>/compute')
def get_collection_cell_data(grid_id, cell_id):
  if grid := GridViewSpec.inflate(grid_id, patch=compute_patch()):
    data = grid.compute_cell_view_spec(cell_id)
    return jsonify(data=data)
  else:
    return jsonify({'error': f"no such set {grid_id}"}), 400


def compute_patch() -> Dict:
  if b64_enc_str := request.args.get('b64_enc_data'):
    try:
      utc_str = base64.b64decode(b64_enc_str)
      return json.loads(utc_str)
    except Exception as e:
      lwar(f"failed to decode b64 data", exc=e)
      return {}
  else:
    return {}


def is_descendant(model: Any, *types: Type) -> bool:
  for valid_type in types:
    if isinstance(model, valid_type):
      return True
  return False
