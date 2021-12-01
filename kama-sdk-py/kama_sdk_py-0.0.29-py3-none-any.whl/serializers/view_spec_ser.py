import base64
import json
from typing import Dict

from kama_sdk.model.base.common import TYPE_KEY
from kama_sdk.model.view.view_group import ViewGroup
from kama_sdk.serializers.common_serializers import ser_meta

from kama_sdk.model.base.model import Model

from kama_sdk.model.view.grid_view_spec import GridViewSpec
from kama_sdk.serializers import common_serializers


def ser_group_meta(view_group: ViewGroup):
  models = view_group.get_collection_specs()
  collection_metas = list(map(ser_grid_minimal_meta, models))
  return {
    **ser_meta(view_group),
    'mode': view_group.get_view_mode(),
    'collection_metas': collection_metas
  }


def ser_grid_minimal_meta(grid_spec: GridViewSpec):
  return {
    **ser_meta(grid_spec),
    TYPE_KEY: grid_spec.get_view_type()
  }


def encode_seed(seed_dict: Dict) -> str:
  utf_json = json.dumps(seed_dict)
  return base64.b64encode(utf_json)


def ser_simple_child(model: Model) -> Dict:
  return common_serializers.ser_meta(model)
