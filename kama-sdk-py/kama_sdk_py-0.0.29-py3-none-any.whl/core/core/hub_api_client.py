from typing import Optional, Dict

import requests

from kama_sdk.utils import env_utils
from kama_sdk.core.core.config_man import config_man

api_path = '/cli'


def backend_host() -> Optional[str]:
  if env_utils.is_dev() or env_utils.is_test():
    if env_utils.is_in_cluster():
      return "http://necthub.com.ngrok.io"
    else:
      return "http://localhost:3000"
  else:
    return 'https://api.nmachine.io'


def post(endpoint, payload, **kwargs) -> requests.Response:
  url = f'{backend_host()}{api_path}{endpoint}'
  print(f"[kama_sdk:hub_client] post {url}")
  return requests.post(
    url,
    json=payload,
    headers=gen_headers(**kwargs)
  )


def patch(endpoint, payload, **kwargs) -> requests.Response:
  url = f'{backend_host()}{api_path}{endpoint}'
  # print(f"[kama_sdk:hub_client] patch {url}")
  return requests.patch(
    url,
    json=payload,
    headers=gen_headers(**kwargs)
  )


def get(endpoint, **kwargs) -> requests.Response:
  url = f'{backend_host()}{api_path}{endpoint}'
  # print(f"[kama_sdk:hub_client] get {url}")
  return requests.get(
    url,
    headers=gen_headers(**kwargs)
  )


def gen_headers(**kwargs) -> Dict:
  access_token = config_man.get_install_token(**kwargs)
  return {
    'Token': access_token
  }
