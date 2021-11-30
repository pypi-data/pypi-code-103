from typing import Any

from kama_sdk.model.base.common import PREDICATE_KEY
from kama_sdk.model.base.mc import ATTR_KW
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.model.predicate.predicate import Predicate


class PredicateResultSupplier(Supplier):

  def predicate(self) -> Predicate:
    return self.inflate_child(Predicate, **{ATTR_KW: PREDICATE_KEY})

  def _compute(self) -> Any:
    predicate = self.predicate()
    return predicate.resolve()
