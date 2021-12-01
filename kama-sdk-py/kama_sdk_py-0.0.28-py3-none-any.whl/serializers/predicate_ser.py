from typing import Dict

from kama_sdk.model.predicate.predicate import Predicate
from kama_sdk.serializers.common_serializers import ser_meta


def ser_predicate(predicate: Predicate) -> Dict:
  return {
    **ser_meta(predicate),
    'space': predicate.get_space_id()
  }
