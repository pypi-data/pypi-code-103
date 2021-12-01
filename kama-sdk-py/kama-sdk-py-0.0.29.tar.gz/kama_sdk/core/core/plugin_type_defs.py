from typing import List, Dict, Type, Any

from typing_extensions import TypedDict

from kama_sdk.core.core.types import KteaDict
from kama_sdk.core.ktea.virtual_ktea_client import VirtualKteaClient
from kama_sdk.model.base.model import Model


class PluginManifest(TypedDict, total=False):
  id: str
  publisher_identifier: str
  app_identifier: str
  model_descriptors: List[Dict]
  asset_paths: List[str]
  model_classes: List[Type[Model]]
  virtual_kteas: List[Type[VirtualKteaClient]]
  shell_bindings: Dict[str, Any]
  verified: bool
  version: str
  prototype_mode_ktea: KteaDict


class SlimPluginManifest(TypedDict):
  id: str
  publisher_identifier: str
  app_identifier: str
  version: str
  prototype_mode_ktea: KteaDict
