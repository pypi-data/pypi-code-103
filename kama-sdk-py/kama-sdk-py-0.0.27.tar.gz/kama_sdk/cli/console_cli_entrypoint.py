import code
import os
from typing import Optional, Dict

import yaml
from k8kat.res.base.kat_res import KatRes
from k8kat.res.config_map.kat_map import KatMap
from k8kat.res.dep.kat_dep import KatDep
from k8kat.res.node.kat_node import KatNode
from k8kat.res.ns.kat_ns import KatNs
from k8kat.res.pod.kat_pod import KatPod
from k8kat.res.pvc.kat_pvc import KatPvc
from k8kat.res.svc.kat_svc import KatSvc
from k8kat.utils.main.api_defs_man import api_defs_man

from kama_sdk.cli import cli_helper
from kama_sdk.core.core import updates_man, job_client, presets_man, status_manager, consts
from kama_sdk.core.core.plugins_manager import plugins_manager
from kama_sdk.core.ktea.vktea_clients_manager import vktea_clients_manager
from kama_sdk.model.base.model import Model
from kama_sdk.utils import utils
from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.ktea.ktea_provider import ktea_client
from kama_sdk.core.telem import backups_manager, flash_helper
from kama_sdk.core.telem.telem_manager import telem_manager
from kama_sdk.model.base.models_manager import models_manager


def get_meta() -> Dict:
  return {
    'name': MODE_NAME,
    'info': 'Start the interactive console'
  }


def register_arg_parser(_):
  """
  Does not accept any options so pass (do nothing).
  :param _:
  :return:
  """
  pass


def run(options):
  cli_helper.start_engines()
  cli_helper.handle_ns(options, MODE_NAME, allow_empty=True)

  context = {
    **make_models_context(),
    **make_k8kat_context(),
    **make_misc_context(),
    **make_v_kteas_context()
  }

  setup_console_history()
  code.interact(None, None, context, None)


def make_models_context():
  return {c.__name__: c for c in models_manager.get_model_classes()}


def make_k8kat_context():
  return {c.__name__: c for c in kat_res_classes}


def make_v_kteas_context():
  return {c.__name__: c for c in vktea_clients_manager.get_clients()}


def make_misc_context():
  return {
    'Model': Model,
    'utils': utils,
    'r': load_dict_from_scratch,
    'config_man': config_man,
    'models_manager': models_manager,
    'updates_man': updates_man,
    'api_defs_man': api_defs_man,
    'status_manager': status_manager,
    'flash_helper': flash_helper,
    'vktea_clients_manager': vktea_clients_manager,
    'telem_manager': telem_manager,
    'backups_manager': backups_manager,
    'job_client': job_client,
    'ktea_client': ktea_client,
    'presets_man': presets_man,
    'plugins_manager': plugins_manager,
    'resolve': resolve,
    'consts': consts
  }


def resolve(expr):
  x = Model({'attr': expr})
  return x.get_attr("attr", depth=100)


def setup_console_history():
  import os as loc_os
  import atexit
  import readline
  import rlcompleter

  history_path = os.path.expanduser("~/.pyhistory")

  def save_history(_history_path=history_path):
    import readline
    readline.write_history_file(_history_path)

  if os.path.exists(history_path):
    readline.read_history_file(history_path)

  atexit.register(save_history)
  del loc_os, atexit, readline, rlcompleter, save_history, history_path


def load_dict_from_scratch(_id: str = None) -> Optional[Dict]:
  scratch_file_path = f"{os.getcwd()}/scratch.yaml"
  with open(scratch_file_path, 'r') as scratch_file:
    model_dicts = list(yaml.full_load_all(scratch_file.read()))
    if _id:
      finder = lambda d: d.get('id') == _id
      if res := next(filter(finder, model_dicts), None):
        return res
      else:
        print(f"[kama_sdk:shell] {_id} not found in {scratch_file_path}")
    else:
      if len(model_dicts) > 0:
        return model_dicts[0]
      else:
        print(f"[kama_sdk:shell] scratch {scratch_file_path} has 0 defs")


kat_res_classes = [
  KatRes,
  KatPod,
  KatDep,
  KatSvc,
  KatPvc,
  KatMap,
  KatNs,
  KatNode
]


MODE_NAME = "console"
