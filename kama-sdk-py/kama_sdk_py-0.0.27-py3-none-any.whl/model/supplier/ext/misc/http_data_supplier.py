from typing import Any

import requests

from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.supplier.base.supplier import Supplier


class HttpDataSupplier(Supplier):

  @model_attr()
  def get_endpoint(self):
    return self.get_attr(ENDPOINT_KEY, missing='warn') or ''

  def _compute(self) -> Any:
    try:
      response = requests.get(self.get_endpoint())
      body_dict = {}
      try:
        body_dict = response.json()
      except:
        pass
      return dict(
        status_code=response.status_code,
        body=body_dict
      )
    except:
      return None


ENDPOINT_KEY = 'endpoint'
