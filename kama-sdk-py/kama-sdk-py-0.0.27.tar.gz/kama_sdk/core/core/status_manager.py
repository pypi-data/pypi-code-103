from datetime import datetime
from typing import Optional, Dict

from kama_sdk.core.core import hub_api_client, consts
from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.core.consts import ERROR_STATUS, RUNNING_STATUS, BROKEN_STATUS
from kama_sdk.core.core.plugins_manager import plugins_manager
from kama_sdk.model.base.mc import STATUS_COMPUTER_LABEL, SPACE_KEY, LABELS_KEY
from kama_sdk.model.predicate.predicate import Predicate
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.utils.logging import lwar, lerr


def compute_all_statuses() -> Dict[str, str]:
  statuses = {}
  for space_id in [consts.APP_SPACE_ID, *plugins_manager.get_plugin_ids()]:
    status = compute_space_status(space_id)
    statuses[space_id] = status
  return statuses


def compute_space_status(space_id) -> str:
  if computer := find_status_computer(space_id):
    try:
      is_positive = computer.resolve()
    except Exception as e:
      lerr(f"status comp for space {space_id}", exc=e)
      return ERROR_STATUS
    return RUNNING_STATUS if is_positive else BROKEN_STATUS
  else:
    lwar(f"space manager {space_id} has no status computer!")
    return ERROR_STATUS


def find_status_computer(space_id: str) -> Optional[Supplier]:
  return Predicate.inflate_single(q={
    SPACE_KEY: space_id,
    LABELS_KEY: {
      STATUS_COMPUTER_LABEL: True
    }
  })


def upload_all_statuses():
  outcomes = {}
  plugin_ids = plugins_manager.get_registered_plugin_ids()
  for space in [consts.APP_SPACE_ID, *plugin_ids]:
    outcomes[space] = upload_status(space=space)
  return outcomes


def full_sync() -> Dict:
  statuses = compute_all_statuses()
  config_man.write_space_statuses(statuses)
  upload_all_statuses()
  return statuses


def upload_status(**kwargs) -> bool:
  if config_man.is_training_mode():
    return False

  config_man.invalidate_cmap()
  status = config_man.get_status(**kwargs)
  ktea = config_man.get_ktea_config(**kwargs)
  kama = config_man.get_kama_config(**kwargs)

  data = {
    'status': status,
    'ktea_type': ktea.get('type'),
    'ktea_version': ktea.get('version'),
    'kama_type': kama.get('type'),
    'kama_version': kama.get('version')
  }

  payload = dict(install=data)
  response = hub_api_client.patch('/install', payload, **kwargs)
  print(f"[kama_sdk:telem_man] upload status resp {response}")
  if success := response.status_code < 205:
    config_man.write_last_status_uploaded(datetime.now())
  return success
