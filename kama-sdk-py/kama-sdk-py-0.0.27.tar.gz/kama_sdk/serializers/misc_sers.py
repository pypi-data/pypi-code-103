from typing import Dict

from kama_sdk.model.k8s.resource_group import ResourceGroup
from kama_sdk.serializers.common_serializers import ser_meta


def ser_victim_group(group: ResourceGroup) -> Dict:
  selectors = group.get_selectors()
  serialized_matchers = [s.as_rest_bundle() for s in selectors]
  return {
    **ser_meta(group),
    'matchers': serialized_matchers
  }
