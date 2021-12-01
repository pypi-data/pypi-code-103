from typing import TypeVar, List, Type, Dict

from typing_extensions import TypedDict

from kama_sdk.model.base.model import Model


T = TypeVar('T', bound='Relation')


class SelectQ(TypedDict, total=False):
  pass


class Relation(Model):

  @classmethod
  def for_left_model(cls, model_cls: Type[Model]):
    pass

  @classmethod
  def select(cls, left_q, right_q) -> List[T]:
    pass


def matches(lookup: Dict, actual: Dict) -> bool:
  lookup_type = lookup.get('type', "model")
  actual_type = actual.get('type', "model")
  is_wildcard = lambda *types: "*" in types

  if lookup_type == actual_type or is_wildcard(lookup_type,  actual_type):
    pass
  else:
    return False
