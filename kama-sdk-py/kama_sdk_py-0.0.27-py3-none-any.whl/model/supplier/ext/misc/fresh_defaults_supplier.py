from typing import Optional, Dict

from kama_sdk.core.ktea.ktea_provider import ktea_client

from kama_sdk.core.core.types import KteaDict

from kama_sdk.model.supplier.base.supplier import Supplier


class FreshDefaultsSupplier(Supplier):

  def get_ktea_dict(self) -> KteaDict:
    return self.get_local_attr(KTEA_KEY, depth=100)

  def _compute(self) -> Optional[Dict]:
    client = ktea_client(
      space=self.get_config_space(),
      ktea=self.get_ktea_dict()
    )
    return client.load_default_values()


KTEA_KEY = 'ktea'
