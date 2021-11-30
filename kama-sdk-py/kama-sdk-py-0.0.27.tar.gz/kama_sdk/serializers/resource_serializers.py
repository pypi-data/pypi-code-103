from typing import Dict

from kama_sdk.model.k8s.variable_category import ResourceCategory
from kama_sdk.model.view.column_spec import ColumnSpec
from kama_sdk.serializers.common_serializers import ser_meta


def ser_col_spec(col_spec: ColumnSpec) -> Dict:
  is_default_visible = col_spec.get_desired_weight() >= 0
  return {
    **ser_meta(col_spec),
    'is_default_visible': is_default_visible
  }


def ser_category(category: ResourceCategory) -> Dict:
  return {
    **ser_meta(category),
    'resource_kinds': category.get_resource_kinds()
  }
