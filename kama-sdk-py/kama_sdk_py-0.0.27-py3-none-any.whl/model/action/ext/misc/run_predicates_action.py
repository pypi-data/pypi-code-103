from typing import List, Optional, Union

from kama_sdk.core.core.types import KoD
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.base.multi_action import MultiAction
from kama_sdk.model.action.ext.misc.run_predicate_action import RunPredicateAction
from kama_sdk.model.base.common import PREDICATE_KEY, PREDICATES_KEY
from kama_sdk.model.base.mc import TITLE_KEY, INFO_KEY, KIND_KEY
from kama_sdk.model.predicate.multi_predicate import MultiPredicate
from kama_sdk.model.predicate.predicate import Predicate

SingleOrMultiPred = Union[Predicate, MultiPredicate]


class RunPredicatesAction(MultiAction):

  def get_title(self) -> Optional[str]:
    return super().get_title() or DEF_TITLE

  def get_info(self) -> Optional[str]:
    return super().get_info() or DEF_INFO

  def get_predicates(self) -> List[Predicate]:
    return self.inflate_children(Predicate, attr=PREDICATES_KEY)

  def _load_sub_actions(self) -> List[Action]:
    kods = [predicate.serialize() for predicate in self.get_predicates()]
    return [self.pred_kod2action(kod) for kod in kods]

  def pred_kod2action(self, predicate_kod: KoD) -> RunPredicateAction:
    action_kod = {PREDICATE_KEY: predicate_kod}
    return self.inflate_child(RunPredicateAction, kod=action_kod)

  @staticmethod
  def from_predicate_subclass(pred: SingleOrMultiPred) -> Optional[KoD]:
    """
    Creates a normalized RunPredicatesAction from either a
    base Predicate or a MultiPredicate. If a MultiPredicate is given,
    each RunPredicate sub_action will map to a predicate. If a normal
    Predicate is given, the single sub_action will come from iti.
    given,
    :param pred: predicate or MultiPredicate
    :return:
    """
    if isinstance(pred, Predicate):
      base = {
        TITLE_KEY: pred.get_title(),
        INFO_KEY: pred.get_info(),
        KIND_KEY: RunPredicatesAction.__name__,
      }
      if isinstance(pred, MultiPredicate):
        configs = [p.get_config() for p in pred.get_sub_predicates()]
        return {**base, PREDICATES_KEY: configs}
      else:
        return {**base, PREDICATES_KEY: [pred.get_config()]}


DEF_TITLE = "Evaluate Predicates"
DEF_INFO = "Run each predicate in the list before proceeding"
