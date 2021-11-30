from typing import Optional, Dict

from k8kat.res.base.kat_res import KatRes

from kama_sdk.model.action.base.action import Action
from kama_sdk.model.base.common import RESOURCE_SELECTOR_KEY, KAT_RES_KEY
from kama_sdk.model.k8s.resource_selector import ResourceSelector


class PatchResourceAction(Action):

  def get_res_selector(self) -> ResourceSelector:
    return self.inflate_child(
      ResourceSelector,
      attr=RESOURCE_SELECTOR_KEY
    )

  def get_kat_res(self) -> Optional[KatRes]:
    if explicit := self._config.get(KAT_RES_KEY):
      return explicit
    else:
      query_results = self.get_res_selector().query_cluster()
      return next(iter(query_results), None)

  def get_patch_contents(self) -> Dict:
    return self.get_local_attr(RESOURCE_PATCH_KEY) or {}

  def perform(self):
    if resource := self.get_kat_res():
      possibly_deep_patch = self.get_patch_contents()
      resource.patch_with_flat_dict(possibly_deep_patch)


RESOURCE_PATCH_KEY = 'resource_patch'
