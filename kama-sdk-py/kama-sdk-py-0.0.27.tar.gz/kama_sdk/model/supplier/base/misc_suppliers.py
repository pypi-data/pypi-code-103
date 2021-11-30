from datetime import datetime
from typing import List, Dict, Any, Optional
from dateutil.parser import parse as parse_date
from kama_sdk.model.base.common import PREDICATE_KEY, VALUE_KEY

from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.predicate.predicate import Predicate, CHALLENGE_KEY
from kama_sdk.utils import utils
from kama_sdk.model.supplier.base.supplier import Supplier, SRC_DATA_KEY
from kama_sdk.utils.logging import lwar


class SumSupplier(Supplier):
  def _compute(self) -> float:
    values = self.get_source_data()
    cleanser = lambda val: float(val or 0)
    return sum(map(cleanser, values))


class ListFlattener(Supplier):
  def _compute(self) -> List:
    source = self.get_source_data()
    cleaner = lambda raw: raw if utils.is_listy(raw) else [raw]
    return utils.flatten(list(map(cleaner, source)))


class ListFilterSupplier(Supplier):

  def get_primed_predicate(self, value: Any) -> Predicate:
    return self.inflate_child(
      Predicate,
      attr=PREDICATE_KEY,
      patch={VALUE_KEY: value},
      weak_patch={CHALLENGE_KEY: value}
    )

  def _compute(self) -> List[Any]:
    keep = []
    for item in self.get_source_data():
      predicate = self.get_primed_predicate(item)
      if predicate.resolve():
        keep.append(item)
    return keep


class ListPluck(Supplier):

  def make_flat(self) -> bool:
    return self.get_attr('flat', backup=False)

  def resolve(self) -> List[Any]:
    included = []
    for it in self._compute():
      predicate_kod, value = it.get('include'), it.get('value')
      predicate_outcome = self.resolve_attr_value(predicate_kod)
      if utils.any2bool(predicate_outcome):
        if self.make_flat() and utils.is_listy(value):
          included += value
        else:
          included.append(value)
    return included


class JoinSupplier(Supplier):

  def items(self) -> List:
    items = self.get_attr("items", lookback=False, backup=[])
    if isinstance(items, list):
      return items
    else:
      lwar(f"{items} is {type(items)}, not list, return []")
      return []

  def separator(self) -> str:
    return self.get_attr("separator", lookback=False, backup=',')

  def _compute(self) -> str:
    if items := self.items():
      return self.separator().join(items)
    else:
      return ""


class MergeSupplier(Supplier):

  def get_sub_dicts(self) -> List[Dict]:
    dicts = self.get_local_attr(SRC_DATA_KEY, depth=100) or [{}]
    return [d or {} for d in dicts]

  def _compute(self) -> Any:
    sub_dicts = self.get_sub_dicts()
    return utils.deep_merge(*sub_dicts)


class UnsetSupplier(Supplier):

  def victim_keys(self) -> List[str]:
    return self.get_attr(VICTIM_KEYS_KEY, backup=[])

  def _compute(self) -> Any:
    victim_keys = self.victim_keys()
    source_dict = self.get_source_data() or {}
    return utils.deep_unset(source_dict, victim_keys)


class FormattedDateSupplier(Supplier):

  def get_source_data(self) -> Optional[datetime]:
    value = super(FormattedDateSupplier, self).get_source_data()
    parse = lambda: parse_date(value)
    return utils.safely(parse) if type(value) == str else value

  def get_output_spec(self):
    return super().get_output_spec() or "%b %d at %I:%M%p %Z"

  def resolve(self) -> Any:
    source = self.get_source_data()
    if type(source) == datetime:
      return source.strftime(self.get_output_spec())
    else:
      return None

class IfThenElseSupplier(Supplier):

  @model_attr()
  def on_true(self) -> Any:
    return self.get_attr(IF_TRUE_KEY)

  @model_attr()
  def on_false(self) -> Any:
    return self.get_attr(IF_FALSE_KEY)

  def get_predicate(self) -> Predicate:
    return self.inflate_child(Predicate, attr=PREDICATE_KEY)

  def _compute(self) -> Any:
    predicate = self.get_predicate()
    positive = predicate.resolve()
    return self.on_true() if positive else self.on_false()


VICTIM_KEYS_KEY = 'victim_keys'
IF_TRUE_KEY = "on_true"
IF_FALSE_KEY = "on_false"
