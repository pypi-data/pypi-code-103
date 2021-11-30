from typing import List

from kama_sdk.core.core.types import KAO
from kama_sdk.model.action.ext.manifest.await_predicates_settled_action import AwaitPredicatesSettledAction
from kama_sdk.model.base.mc import TITLE_KEY, INFO_KEY
from kama_sdk.model.predicate.kaos2preds import kaos2predicates
from kama_sdk.model.predicate.predicate import Predicate


class AwaitKaosSettledAction(AwaitPredicatesSettledAction):

  def get_id(self) -> str:
    return super().get_id() or DEFAULT_ID

  def get_title(self) -> str:
    return self.get_local_attr(TITLE_KEY) or DEFAULT_TITLE

  def get_info(self) -> str:
    return self.get_local_attr(INFO_KEY) or DEFAULT_INFO

  def get_kaos(self) -> List[KAO]:
    return self.get_attr(KAOs_KEY)

  def get_predicates(self) -> List[Predicate]:
    return kaos2predicates(self.get_kaos())


DEFAULT_ID = "sdk.action.await_kaos_settled"
DEFAULT_TITLE = "Wait for changed resources to settle"
DEFAULT_INFO = "Wait until all changed resource are in a settled state"
KAOs_KEY = "kaos"
