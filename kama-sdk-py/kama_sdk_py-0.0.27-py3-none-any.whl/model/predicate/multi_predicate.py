from typing import List, TypeVar

from kama_sdk.model.base import mc
from kama_sdk.model.base.common import PREDICATES_KEY
from kama_sdk.model.predicate.predicate import Predicate, OPERATOR_KEY

OWN_T = TypeVar('OWN_T', bound='MultiPredicate')

class MultiPredicate(Predicate):

  def get_sub_predicates(self) -> List[Predicate]:
    """
    Returns a list of Predicate instances inflated from
    the value of the 'predicates' attribute.
    :return:
    """
    kwargs = {mc.ATTR_KW: PREDICATES_KEY}
    return self.inflate_children(Predicate, **kwargs)

  def get_operator(self):
    return self.get_attr(OPERATOR_KEY, backup='and')

  def resolve(self) -> bool:
    """
    Resolves the sub-predicates one by one, halting depending
    on the result and the logical operator (e.g a False halts if
    the operator is 'and').
    :return:
    """
    operator = self.get_operator()

    for predicate in self.get_sub_predicates():
      resolved_to_true = predicate.resolve()

      if operator == 'or':
        if resolved_to_true:
          return True
      elif operator == 'and':
        if not resolved_to_true:
          return False
      else:
        print(f"[kama_sdk::multi_pred] illegal operator {operator}")
        return False
    return operator == 'and'

  @classmethod
  def from_predicate_instances(cls: OWN_T, predicates: List[Predicate]) -> OWN_T:
    configs = [p.get_config() for p in predicates]
    return cls.inflate({PREDICATES_KEY: configs})
