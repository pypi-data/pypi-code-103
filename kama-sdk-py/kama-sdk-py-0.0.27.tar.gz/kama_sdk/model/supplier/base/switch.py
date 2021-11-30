from typing import Optional, Any, List, Dict

from kama_sdk.model.base.common import PREDICATE_KEY, VALUE_KEY
from typing_extensions import TypedDict

from kama_sdk.core.core.types import KoD
from kama_sdk.model.base import mc
from kama_sdk.model.supplier.base import supplier
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.model.predicate.predicate import Predicate


class SwitchItemBundle(TypedDict):
  predicate: Predicate
  value: Any


class Switch(Supplier):

  def item2bundle(self, item: Dict) -> SwitchItemBundle:
    kod = item.get(PREDICATE_KEY)
    kwargs = {mc.KOD_KW: kod, mc.INFLATE_SAFELY_KW: True}
    predicate = self.inflate_child(Predicate, **kwargs)
    return {VALUE_KEY: item.get(VALUE_KEY), PREDICATE_KEY: predicate}

  def get_source_data(self) -> List[SwitchItemBundle]:
    raw = super(Switch, self).get_source_data()
    items = self.type_check(supplier.SRC_DATA_KEY, raw, list, alt=[])
    return [self.item2bundle(item) for item in items]

  def resolve(self) -> Optional[KoD]:
    for bundle in self.get_source_data():
      if predicate := bundle['predicate']:
        if predicate.resolve():
          return self.resolve_attr_value(bundle['value'])
    return None
