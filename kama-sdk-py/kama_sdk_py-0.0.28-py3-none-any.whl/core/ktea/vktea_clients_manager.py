from typing import List, Optional, Type

from kama_sdk.core.ktea.virtual_ktea_client import VirtualKteaClient
from kama_sdk.misc.inline_injections_vktea import InlineInjectionsVktea


class VirtualKteaClientsMan:
  def __init__(self):
    self._virtual_kteas: List[Type[VirtualKteaClient]] = []

  def register_client(self, virtual_ktea_client: Type[VirtualKteaClient]):
    self._virtual_kteas.append(virtual_ktea_client)

  def find_client(self, **kwargs) -> Optional[Type[VirtualKteaClient]]:
    name = kwargs.pop('name', None)
    if name:
      matcher = lambda vc: vc.__name__ == name
      return next(filter(matcher, self._virtual_kteas), None)
    return None

  def clear(self, restore_defaults=True):
    self._virtual_kteas = []
    if restore_defaults:
      self.register_defaults()

  def get_clients(self):
    return self._virtual_kteas

  def register_defaults(self):
    self.register_client(InlineInjectionsVktea)


vktea_clients_manager = VirtualKteaClientsMan()
