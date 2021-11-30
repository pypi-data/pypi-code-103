import base64
from typing import Dict, Optional, List

from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.ktea.virtual_ktea_client import VirtualKteaClient


class InlineInjectionsVktea(VirtualKteaClient):

  def _template(self, values: Dict) -> List[Dict]:
    return [
      template(config_man.get_ns(), values or {})
    ]


def template(ns: str, values: Dict) -> Dict:
  return {
    'apiVersion': 'v1',
    'kind': 'Secret',
    'metadata': {
      'name': 'nmachine-injections',
      'namespace': ns
    },
    'data': {k: encode_value(v) for k, v in values.items()}
  }


def encode_value(value: Optional[str]) -> str:
  as_ascii = (value or "").encode('ascii')
  return base64.b64encode(as_ascii).decode('ascii')
