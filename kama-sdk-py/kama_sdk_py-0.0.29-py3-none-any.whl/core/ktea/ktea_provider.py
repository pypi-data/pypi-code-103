from typing import Type

from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.core.consts import KTEA_TYPE_LOCAL_EXEC, KTEA_TYPE_VIRTUAL, APP_SPACE_ID, KTEA_TYPE_SERVER, \
  KTEA_TYPE_MNG_SERVER
from kama_sdk.core.ktea.http_ktea_client import HttpKteaClient
from kama_sdk.core.ktea.ktea_client import KteaClient
from kama_sdk.core.ktea.local_exec_ktea_client import LocalExecKteaClient
from kama_sdk.core.ktea.vktea_clients_manager import vktea_clients_manager


def ktea_client(**kwargs) -> KteaClient:
  space = kwargs.get('space')
  ktea = kwargs.get('ktea')

  if not ktea:
    space = space or APP_SPACE_ID
    ktea = config_man.get_ktea_config(space=space)

  client_class = find_client_class(ktea)
  return client_class(ktea, space)

def find_client_class(ktea) -> Type[KteaClient]:
  ktea_type = ktea['type']

  if ktea_type in server_types:
    return HttpKteaClient
  elif ktea_type == KTEA_TYPE_LOCAL_EXEC:
    return LocalExecKteaClient
  elif ktea_type == KTEA_TYPE_VIRTUAL:
    klass_or_name = ktea['uri']
    if type(klass_or_name) == type:
      klass = klass_or_name
    elif type(klass_or_name) == str:
      klass = vktea_clients_manager.find_client(name=klass_or_name)
    else:
      raise Exception(f"[ktea_provider] invalid ktea uri {klass_or_name}")
    return klass
  else:
    raise RuntimeError(f"Illegal KTEA type {ktea_type}")


server_types = [KTEA_TYPE_SERVER, KTEA_TYPE_MNG_SERVER]
