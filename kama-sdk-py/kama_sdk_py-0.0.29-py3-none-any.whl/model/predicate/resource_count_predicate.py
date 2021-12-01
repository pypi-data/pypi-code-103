from kama_sdk.model.k8s import resource_selector
from kama_sdk.model.k8s.resource_selector import ResourceSelector
from kama_sdk.model.predicate import predicate
from kama_sdk.model.predicate.predicate import Predicate


class ResourceCountPredicate(Predicate):

  def attr_fwd_bundle(self):
    attrs = self._config.items()
    return {k: v for k, v in attrs if k in forwardable_attr_keys}

  def get_challenge(self) -> int:
    selector = self.inflate_child(
      ResourceSelector,
      kod=self.attr_fwd_bundle()
    )
    return len(selector.query_cluster())

  def get_check_against(self) -> int:
    if explicit := self.get_attr(predicate.CHECK_AGAINST_KEY):
      return explicit
    else:
      return 1


forwardable_attr_keys = [
  resource_selector.RES_KIND_KEY,
  resource_selector.RES_NAME_KEY,
  resource_selector.RES_NS_KEY,
  resource_selector.LABEL_SEL_KEY,
  resource_selector.NOT_LABEL_SEL_KEY,
  resource_selector.FIELD_SEL_KEY
]
