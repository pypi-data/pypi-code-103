import json
from typing import Dict, List, Type

from k8kat.auth.kube_broker import broker
from kubernetes.client import V1ConfigMap, V1ObjectMeta

from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.core.consts import KAMAFILE, APP_SPACE_ID, KTEA_TYPE_VIRTUAL
from kama_sdk.core.core.types import KAOs
from kama_sdk.core.ktea.ktea_client import KteaClient
from kama_sdk.core.ktea.virtual_ktea_client import VirtualKteaClient
from kama_sdk.core.ktea.vktea_clients_manager import vktea_clients_manager
from kama_sdk.model.operation.operation_state import OperationState
from kama_sdk.model.operation.step_state import StepState


http_ktea_uri = "https://api.nmachine.io/ktea/nmachine/hello-ktea"


def http_ktea_uri_with_ver():
  return "https://api.nmachine.io/ktea/nmachine/hello-ktea/1.0.0"


def ci_kteale_name():
  return "wiz-ci-ktea-eval"


def one_step_state(step, keep=True) -> StepState:
  op_state = OperationState('123', 'abc')
  return op_state.gen_step_state(step, keep)


def mock_globals(ns):
  if ns:
    config_man._ns = ns


def create_base_kamafile(ns):
  broker.coreV1.create_namespaced_config_map(
    namespace=ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(
        namespace=ns,
        name=KAMAFILE
      ),
      data={
        APP_SPACE_ID: json.dumps({})
      }
    )
  )


def clear_telem_db():
  # todo rewrite!
  print(f"clear_telem_db SOMEONE RE-WRITE ME PLEASE")
  # if database := telem_man.create_session_if_none():
  #   if str(database.name).startswith("test_"):
  #     for collection in list(database.list_collections()):
  #       database.drop_collection(collection['name'])
  #   else:
  #     raise RuntimeError("[kama_sdk] attempted to drop non-test telem db!")


def write_cman_foo_bar_user_vars():
  """
  Common data for tests.
  :return:
  """
  config_man.patch_user_vars({'foo': 'bar', 'bar': {'foo': 'baz'}})


class IdentityConfigMapVirtualKtea(VirtualKteaClient):
  """
  Convenience virtual KTEA whose template output is a
  constant ConfigMap whose data is equal to the values that
  get passed to it. Typically, your tests will want to make
  sure that the `data` as  you passed it.
  """
  def _template(self, values: Dict) -> List[Dict]:
    return [
      {
        'apiVersion': 'v1',
        'kind': 'ConfigMap',
        'metadata': {
          'name': 'foo',
          'annotations': {'v': '1'},
          'namespace': self.release_name()
        },
        'data': values
      }
    ]

  def _default_values(self) -> Dict:
    return {'k': '1'}


class Sec2ValVirtualKtea(VirtualKteaClient):
  def _template(self, values: Dict) -> List[Dict]:
    return [
      {
        'apiVersion': 'v1',
        'kind': 'ConfigMap',
        'metadata': {
          'name': 'fake-secret',
          'namespace': self.release_name()
        },
        'data': values
      }
    ]


def set_and_register_trivial_vtam():
  set_and_register_vktea(IdentityConfigMapVirtualKtea)


def clear_trivial_vtam():
  vktea_clients_manager.clear()


def set_and_register_vktea(vktea_cls: Type[VirtualKteaClient]):
  vktea_clients_manager.register_client(vktea_cls)
  config_man.write_ktea(dict(
    type=KTEA_TYPE_VIRTUAL,
    uri=vktea_cls.__name__
  ))


def g_conf(**kwargs):
  key = kwargs.pop('k', 'key')

  return dict(
    id=key,
    kind=kwargs.pop('i', 'kind'),
    title=kwargs.pop('t', f'{key}.title'),
    info=kwargs.pop('d', f'{key}.desc'),
    **kwargs
  )


def cmap_descriptor(ns: str, data=None):
  data = {} if data is None else data
  return dict(
    apiVersion='v1',
    kind='ConfigMap',
    metadata=dict(name='cm-good', namespace=ns),
    data=data
  )


def ktea_apply_cmap(ns: str) -> KAOs:
  return KteaClient.kubectl_apply([
    cmap_descriptor(ns)
  ])

def bad_cmap_kao(ns: str) -> KAOs:
  return KteaClient.kubectl_apply([
    dict(
      apiVersion='v1',
      kind='ConfigMap',
      metadata=dict(name='cm-bad', namespace=ns),
      data='wrong-format'
    )
  ])

def ktea_apply_pod(**kwargs) -> KAOs:
  return KteaClient.kubectl_apply([
    dict(
      apiVersion='v1',
      kind='Pod',
      metadata=dict(
        name=kwargs.get('name', 'pod'),
        namespace=kwargs['ns']
      ),
      spec=dict(
        containers=[
          dict(
            name='main',
            image=kwargs.get('image', 'nginx')
          )
        ]
      )
    )
  ])
