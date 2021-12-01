from typing import Dict, Optional

from k8kat.auth.kube_broker import broker
from k8kat.res.ns.kat_ns import KatNs

from kama_sdk.core.core import config_man, config_man_helper
from kama_sdk.core.ktea.vktea_clients_manager import vktea_clients_manager
from kama_sdk.model.base import static_validator
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.utils.logging import lwar, lwin


def warn_ns_not_set():
  pass


def start_engines(validate=True):
  models_manager.add_defaults()
  config_man_helper.clear_trackers()
  vktea_clients_manager.register_defaults()
  if validate:
    static_validator.run_all()


def handle_ns(options: Dict, proc: str, allow_empty=False):
  if broker.is_connected:
    if mock_ns := options.get(MOCK_NAMESPACE_FLAG):
      ns = mock_ns
    else:
      if broker.is_in_cluster_auth():
        ns = read_file_ns()
      else:
        ns = config_man.read_dev_file_ns()
    if ns:
      if KatNs.find(ns):
        if not broker.is_in_cluster_auth():
          config_man.coerce_ns(ns)
        lwin(f"KAMA {proc} started (namespace={ns})")
      else:
        if allow_empty:
          lwar(f"Starting {proc} with with non-existent namespace {ns}")
        else:
          raise RuntimeError(f"Cannot start {proc}: namespace "
                             f"'{ns}' does not exist")
    else:
      if allow_empty:
        lwar(f"Proceeding without ns; set with --n <name>")
      else:
        message = f"Cannot start {proc} process without namespace. " \
                  f"Try again with -n <namespace>"
        raise RuntimeError(message)
  else:
    lwar(f"Starting {proc} without Kubernetes connection!")


def read_file_ns() -> Optional[str]:
  try:
    with open(_ns_path, 'r') as file:
      if contents := file.read():
        return contents.strip()
      return None
  except FileNotFoundError:
    return None


_ns_path = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
MOCK_NAMESPACE_FLAG = "namespace"
