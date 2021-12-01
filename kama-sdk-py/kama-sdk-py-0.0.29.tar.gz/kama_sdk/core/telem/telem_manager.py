from copy import deepcopy
from typing import Optional, Dict, List, Type

from kama_sdk.core.core import hub_api_client
from kama_sdk.core.core.types import ErrorCapture, EventCapture
from kama_sdk.core.telem import flash_helper
from kama_sdk.core.telem.telem_backend import TelemBackend

"""
Module responsible for handling requests to register, persist, and/or 
upload telemetry data. Telemetry data may either be 
events (EventCapture schema) or errors (ErrorCapture). 

When a caller (e.g an Action) creates telemetry, it starts by calling
`register_event/error`, which writes a serialized version of the event
to a temporary JSON file called the "flash". The flash must be persisted
because callers may run in different processes. A better implementation
may be   

"""


synced_key = 'synced'
primary_key = '_id'

events_coll_id = 'events'
backups_coll_id = 'config_backups'
errors_coll_id = 'errors'

class TelemManager:

  _backend_inst: Optional[TelemBackend]

  def __init__(self):
    self._backend_inst = None

  def set_backend_class(self, backend_cls: Type[TelemBackend]):
    self._backend_inst = backend_cls()

  def get_backend(self) -> Optional[TelemBackend]:
    return self._backend_inst

  def is_enabled(self) -> bool:
    if backend := self.get_backend():
      return backend.is_enabled()
    return False

  def is_online(self) -> bool:
    if backend := self.get_backend():
      if backend.is_enabled():
        return backend.is_online()
    return False

  def flush_flash(self):
    backend = self.get_backend()
    for collection_id in [events_coll_id, errors_coll_id]:
      for record in flash_helper.read_collection(collection_id):
        is_synced = upload_item(collection_id, record)
        record[synced_key] = is_synced
        if backend:
          backend.create_record(collection_id, record)
      flash_helper.write_collection(collection_id, [])

  def create_backup_record(self, backup: Dict) -> Optional[Dict]:
    if backend := self.get_backend():
      return backend.create_record(backups_coll_id, backup)

  @staticmethod
  def register_event(event: EventCapture):
    """
    Given an event, stores the event in the temporary flash storage
    for later definitive handling.
    :param event: dict
    """
    flash_helper.push_record(events_coll_id, event)

  @staticmethod
  def register_error(error: ErrorCapture):
    flash_helper.push_record(errors_coll_id, error)

  @staticmethod
  def clear_flash():
    flash_helper.clear()

  @staticmethod
  def get_events_in_flash() -> List[Dict]:
    return flash_helper.read_collection(events_coll_id)

  @staticmethod
  def get_errors_in_flash() -> List[Dict]:
    return flash_helper.read_collection(errors_coll_id)

  def flush_persistent_store(self):
    if backend := self.get_backend():
      for coll_id in [events_coll_id, errors_coll_id]:
        records = backend.query_collection(coll_id, {synced_key: False})
        for record in records:
          if upload_item(coll_id, record):
            record[synced_key] = True
            backend.update_record(coll_id, record)


def upload_item(collection_name: str, item) -> bool:
  hub_key = f'kama_{collection_name}'[0:-1]
  clean_item = deepcopy(item)
  clean_item.pop(primary_key, None)
  clean_item.pop(synced_key, None)
  resp = hub_api_client.post(f'/{hub_key}s', {hub_key: clean_item})
  return resp.status_code == 400


telem_manager = TelemManager()
