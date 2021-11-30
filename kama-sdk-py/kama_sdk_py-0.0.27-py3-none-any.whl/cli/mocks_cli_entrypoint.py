import json
from argparse import ArgumentParser
from typing import Dict, List

from k8kat.auth.kube_broker import broker
from k8kat.res.config_map.kat_map import KatMap
from k8kat.res.ns.kat_ns import KatNs
from kubernetes.client import V1Namespace, V1ObjectMeta, V1ConfigMap

from kama_sdk.cli import cli_helper
from kama_sdk.core.core import config_man as cm
from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.core.consts import KAMAFILE, APP_SPACE_ID, KTEA_TYPE_SERVER

from kama_sdk.core.core.types import KteaDict, KamaDict
from kama_sdk.core.ktea.ktea_provider import ktea_client
from kama_sdk.utils import utils, logging
from kama_sdk.utils.logging import lerr, lwar


def get_meta() -> Dict:
  return {'name': 'mock-install', 'info': 'Mock an installation'}


def run(options: Dict):
  namespace = options.get(NAMESPACE_FLAG)
  overrides_raw: List[str] = options.get(SET_FLAG) or []

  force = options.get(FORCE_FLAG, False)
  port = options.get(PORT_FLAG) or 5000
  pop_defaults = options.get(POPULATED_FLAG, False)

  config = compile_config(overrides_raw, port)
  create_ns_if_missing(namespace)
  if delete_cmap_if_exists(namespace, force):
    create_mocked_cmap(namespace, config)
    cm.coerce_ns(namespace)
    if pop_defaults:
      populate_defaults()
    logging.lwin(f"created configmap/{KAMAFILE} in namespace {namespace}")
  else:
    err = f"ConfigMap already exists, use --{FORCE_FLAG} to overwrite"
    lerr(err, sig="kama_sdk")


def populate_defaults():
  cli_helper.start_engines(validate=False)
  defaults = ktea_client().load_default_values()
  config_man.write_default_vars(defaults)


def compile_config(overrides_raw: List[str], port) -> Dict:
  overrides_fdicts = list(map(str_assign_2_flat, overrides_raw))
  overrides_dict = utils.deep_merge_flats(overrides_fdicts)

  default_config = gen_default_config(port)

  final_dict = utils.deep_merge(default_config, overrides_dict)
  return format_bundle(final_dict)


def delete_cmap_if_exists(namespace: str, force: bool) -> bool:
  if cmap := KatMap.find(KAMAFILE, namespace):
    if force:
      lwar(f"deleting exsiting namespaces/{namespace}")
      cmap.delete(wait_until_gone=True)
    else:
      return False
  return True


def format_bundle(bundle: Dict) -> Dict:
  new_bundle = {}
  for key, value in bundle.items():
    serialized_value = cm.type_serialize_entry(key, value)
    new_bundle[key] = serialized_value
  return new_bundle


def str_assign_2_flat(str_assign: str) -> Dict:
  deep_key, value = str_assign.split("=")
  return {deep_key: value}


def register_arg_parser(parser: ArgumentParser):
  parser.add_argument(
    NAMESPACE_FLAG,
    help="Namespace/release name"
  )

  parser.add_argument(
    f"--{POPULATED_FLAG}",
    action="store_true",
    help=f"Populate defaults values from the given KTEA"
  )

  parser.add_argument(
    f"--{SET_FLAG}",
    action='append',
    help=f"Assignment into configmap/{KAMAFILE}"
  )

  parser.add_argument(
    f"--{FORCE_FLAG}",
    action="store_true",
    help=f"Delete namespace if it already exists"
  )

  parser.add_argument(
    f"--{PORT_FLAG}",
    help=f"KAMA prototype server port, defaults to 5000"
  )


def create_ns_if_missing(name: str):
  if existing := KatNs.find(name):
    existing.label(True, managed_by='nmachine')
    return existing.reload()
  else:
    return broker.coreV1.create_namespace(
      body=V1Namespace(
        metadata=V1ObjectMeta(
          name=name,
          labels={'managed_by': 'nmachine'}
        )
      )
    )


def create_mocked_cmap(namespace: str, app_config: Dict):
  broker.coreV1.create_namespaced_config_map(
    namespace,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(
        name=KAMAFILE,
        namespace=namespace,
        labels={
          'managed_by': 'nmachine'
        }
      ),
      data={
        APP_SPACE_ID: json.dumps(app_config)
      }
    )
  )


def gen_default_config(port_num: int) -> Dict:
  return {
    cm.INSTALL_ID_KEY: '',
    cm.IS_PROTOTYPE_KEY: True,
    cm.STATUS_KEY: 'installing',

    cm.KTEA_CONFIG_KEY: KteaDict(
      type=KTEA_TYPE_SERVER,
      uri="https://api.nmachine.io/ktea/nmachine/ice-kream-ktea",
      version='1.0.1'
    ),

    cm.KAMA_CONFIG_KEY: KamaDict(
      type=KTEA_TYPE_SERVER,
      uri=f"http://localhost:{port_num}",
      version="latest"
    ),

    cm.USER_VARS_LVL: {},
    cm.USER_INJ_VARS_LVL: {},
    cm.DEF_VARS_LVL: {},
  }


NAMESPACE_FLAG = "namespace"
SET_FLAG = "set"
FORCE_FLAG = "force"
POPULATED_FLAG = "populated"
PORT_FLAG = "port"
