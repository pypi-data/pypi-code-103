from typing import List, Optional

from k8kat.res.base.kat_res import KatRes

from kama_sdk.model.action.base.multi_action import MultiAction
from kama_sdk.model.action.ext.k8s.delete_resource_action import DeleteResourceAction, TREAT_MISSING_AS_FATAL_KEY, \
  WAIT_TIL_GONE_KEY, KAT_RES_KEY
from kama_sdk.model.base.common import RESOURCE_SELECTORS_KEY
from kama_sdk.model.base.mc import ID_KEY
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.k8s.resource_selector import ResourceSelector
from kama_sdk.utils import utils


class DeleteResourcesAction(MultiAction):

  def get_resource_selectors(self) -> List[ResourceSelector]:
    return self.inflate_children(
      ResourceSelector,
      attr=RESOURCE_SELECTORS_KEY
    )

  def get_title(self) -> Optional[str]:
    explicit = super(DeleteResourcesAction, self).get_title()
    return explicit or DEF_TITLE

  def get_info(self) -> Optional[str]:
    explicit = super(DeleteResourcesAction, self).get_info()
    return explicit or DEF_INFO

  def _load_sub_actions(self) -> List[DeleteResourceAction]:
    """
    For each victim resource, generate a DeleteResourceAction
    :return:
    """
    resources = self.compute_victim_resources()
    deletion_actions = [self.katres2action(r) for r in resources]
    return deletion_actions

  @model_attr(cached=True)
  def compute_victim_resources(self) -> List[KatRes]:
    """
    Iterate over resource selectors, for each, query cluster to get
    corresponding KatRes's. Returned flattened list of lists.
    :return:
    """
    results = [s.query_cluster() for s in self.get_resource_selectors()]
    return utils.flatten(results)

  def katres2action(self, kat_res: KatRes) -> DeleteResourceAction:
    copy_attrs = [TREAT_MISSING_AS_FATAL_KEY, WAIT_TIL_GONE_KEY]
    config = {
      ID_KEY: f"{self.get_id()}.{kat_res.kind}.{kat_res.name}",
      KAT_RES_KEY: kat_res,
      **utils.subdict(self.get_config(), *copy_attrs)
    }
    child = DeleteResourceAction(config)
    child.set_parent(self)
    return child
    # return self.inflate_child(DeleteResourceAction, kod=config)


DEF_TITLE = "Delete selected resources"
DEF_INFO = "Delete resources one by one, wait for non-existence"
