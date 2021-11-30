from typing import Dict

from kama_sdk.model.base.model import Model


def ser_meta(model: Model) -> Dict:
  return {
    'id': model.get_id(),
    'title': model.get_title(),
    'info': model.get_info()
  }
