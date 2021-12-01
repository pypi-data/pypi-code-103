from typing import List

from kama_sdk.model.base.common import RESOURCE_SELECTORS_KEY
from kama_sdk.model.base.model import Model
from kama_sdk.model.k8s.resource_selector import ResourceSelector


class ResourceGroup(Model):
  def get_selectors(self) -> List[ResourceSelector]:
    return self.inflate_children(
      ResourceSelector,
      attr=RESOURCE_SELECTORS_KEY
    )
