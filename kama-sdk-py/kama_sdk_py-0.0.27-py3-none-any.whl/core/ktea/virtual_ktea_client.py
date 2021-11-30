from typing import List, Dict

from kama_sdk.core.core.types import K8sResDict
from kama_sdk.core.ktea.ktea_client import KteaClient


class VirtualKteaClient(KteaClient):
  def template_manifest(self, values: Dict) -> List[K8sResDict]:
    return self._template(values)

  def load_default_values(self) -> Dict[str, str]:
    return self._default_values()

  def _template(self, values: Dict) -> List[Dict]:
    raise NotImplementedError

  def _default_values(self) -> Dict:
    return {}
