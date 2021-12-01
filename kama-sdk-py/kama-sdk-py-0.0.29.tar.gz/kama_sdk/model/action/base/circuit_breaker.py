from kama_sdk.core.core.consts import POS_STATUS, NEG_STATUS
from kama_sdk.model.base.common import PREDICATE_KEY
from kama_sdk.model.base.model import Model
from kama_sdk.model.predicate.predicate import Predicate
from kama_sdk.utils.logging import lwar


class CircuitBreaker(Model):

  def get_on_index(self) -> int:
    return int(self.get_attr(ON_INDEX_KEY))

  def get_predicate(self) -> Predicate:
    return self.inflate_child(Predicate, attr=PREDICATE_KEY)

  def is_triggered(self) -> bool:
    return self.get_predicate().resolve()

  def matches_action(self, index: int) -> bool:
    return self.get_on_index() == index

  def get_exit_status(self):
    value = self.get_attr(EXIT_STATUS_KEY) or POS_STATUS
    if value in [POS_STATUS, NEG_STATUS]:
      return value
    else:
      lwar(f"bad exit status '{value}', using {POS_STATUS}", sig=self.sig())
      return POS_STATUS


EXIT_STATUS_KEY = "status"
ON_INDEX_KEY = 'on_index'
