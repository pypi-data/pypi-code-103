import json
import os
import sys
from datetime import datetime
from json import JSONDecodeError
from typing import Optional, Dict, Any, List

from k8kat.res.config_map.kat_map import KatMap
from k8kat.utils.main.utils import deep_merge

from kama_sdk.core.core import config_man_helper as helper, consts
from kama_sdk.core.core.consts import KAMAFILE
from kama_sdk.core.core.types import KteaDict, KamaDict
from kama_sdk.utils import utils, env_utils
from kama_sdk.utils.logging import lerr, lwar


class ConfigMan:
  """
  Core KAMA module. Provides a safe access interface to to the underlying
  Kubernetes ConfigMap ('kamafile') which the KAMA uses to persist
  state. A singleton instance of ConfigMan is created on startup
  (see entrypoint.py docs). Always use the singleton instance, never
  instantiate your own.

  Beyond standard I/O with the ConfigMap, the ConfigMan has the following
  notable logic:
  - Caching. ConfigMan uses caching mechanism to only reload the underlying
    ConfigMap when necessary.
  - Type checking. Ensures that requests to write fields only go through
    if the values match the expected type. It also serializes some types.
  """

  _cmap: Optional[KatMap]
  _ns = Optional[str]

  def __init__(self):
    self._cmap = None
    self._ns = None

  def invalidate_cmap(self):
    self._cmap = None

  def get_ns(self):
    if not self._ns:
      self._ns = _read_ns()
      if not self._ns:
        print("[kama_sdk:config_man:ns] failed to read new NS")
    return self._ns

  def load_source_cmap(self, **kwargs) -> Optional[KatMap]:
    """
    Returns the underlying ConfigMap wrapped for convenience in
    a KatMap. If the ConfigMap is cached and clean (no writes since
    last lookup), the cached version will be returned. You can force
    ignore the cache by passing reload=True in the kwargs. Should
    not be called by the user.
    :param kwargs:
    :return:
    """
    if ns := self.get_ns():
      if self.should_reload_source(**kwargs):
        if fresh_cmap := helper.do_load_cmap(ns):
          helper.track_cmap_read(ns)
        self._cmap = fresh_cmap
      self._log_if_nil_source_after_reload()
      return self._cmap
    else:
      lerr("load_master_cmap namespace nil!")
      return None

  def should_reload_source(self, **kwargs):
    """
    Convenience method for calling helper.should_reload_cmap.
    :param kwargs:
    :return: output of helper.should_reload_cmap
    """
    reload_strategy = kwargs.pop('reload', None)
    return helper.should_reload_cmap(
      self._cmap,
      self.get_ns(),
      reload_strategy
    )

  def read_spaces(self, **kwargs) -> Dict:
    result = {}
    if cmap := self.load_source_cmap(**kwargs):
      data = cmap.data or {}
      for space_id, enc_body in list(data.items()):
        decoded_body = {}
        try:
          decoded_body = json.loads(enc_body or '{}')
        except JSONDecodeError:
          lwar(f"read failed on corrupt space: {enc_body}")
        result[space_id] = decoded_body
      return result
    else:
      lerr("read_space - kamafile was not, returning {}")
      return {}

  def read_space(self, **kwargs) -> Dict:
    """
    Returns the entire config bundle for a space.
    See load_source_cmap docs for details about caching behavior. Uses
    the 'space' from the kwargs if present, otherwise the default 'app'.
    :param kwargs:
    :return:
    """
    if spaces := self.read_spaces(**kwargs):
      space_id = kwargs.get(SPACE_KW) or consts.APP_SPACE_ID
      return spaces.get(space_id) or {}

  def write_space(self, new_value: Dict, **kwargs):
    """
    Overwrites the entire space bundle for a given space with the given
    value. Should probably never be invoked directly by an outside caller.
    If the write fails, we're basically boned; need a 'is_in_bad_state'
    controllers should call every request.
    :param new_value: Dict to replace the current value
    :param kwargs:
    :return:
    """
    if cmap := self.load_source_cmap(**kwargs):
      space_id = kwargs.get(SPACE_KW) or consts.APP_SPACE_ID
      try:
        json_encoded_space = json.dumps(new_value)
        cmap.raw.data[space_id] = json_encoded_space
        cmap.touch(save=True)
        helper.track_cmap_write(self.get_ns())
      except JSONDecodeError:
        lwar(f"write failed on corrupt space: {new_value}")
    else:
      lerr("write impossible, no cmap")

  def read_entry(self, key: str, **kwargs) -> Any:
    """
    Given a key and a space, returns the raw (not type-transformed)
    value indexed by that key in that space. Default space used if none
    passed.
    :param key: key from config bundle
    :param kwargs:
    :return:
    """
    return self.read_space(**kwargs).get(key)

  def write_entry(self, key: str, serialized_value, **kwargs):
    self.write_entries({key: serialized_value}, **kwargs)

  def write_entries(self, serialized_assignments, **kwargs):
    space = self.read_space(**kwargs)
    updated_space = {**space, **serialized_assignments}
    self.write_space(updated_space, **kwargs)

  def write_typed_entries(self, assigns: Dict, **kwargs):
    func = type_serialize_entry
    ser_assignments = {k: func(k, v) for k, v in assigns.items()}
    self.write_entries(ser_assignments, **kwargs)

  def write_typed_entry(self, key: str, value: Any, **kwargs):
    self.write_typed_entries({key: value}, **kwargs)

  def read_typed_entry(self, key: str, **kwargs) -> Any:
    raw_value = self.read_entry(key, **kwargs)
    type_mapping = schema.get(key)
    value = helper.parse_inbound(raw_value, type_mapping)
    if value is not None:
      return value
    else:
      backup = backup_mappings.get(type_mapping)
      return backup if backup is not None else value

  def _read_dict(self, key: str, **kwargs) -> Dict:
    return self.read_entry(key, **kwargs) or {}

  def patch_into_deep_dict(self, dict_key: str, _vars: Dict, **kwargs):
    crt_dict = self._read_dict(dict_key, **kwargs)
    new_dict = deep_merge(crt_dict, utils.flat2deep(_vars))
    self.write_typed_entry(dict_key, new_dict, **kwargs)

  def unset_deep_vars(self, dict_key: str, var_keys: List[str], **kwargs):
    crt_dict = self._read_dict(dict_key, **kwargs)
    flat_dict = utils.deep2flat(crt_dict)
    for victim_var_key in var_keys:
      flat_dict.pop(victim_var_key, None)
    updated_dict = utils.flat2deep(flat_dict)
    self.write_typed_entry(dict_key, updated_dict)

  def get_app_id(self, **kwargs) -> str:
    return self.read_typed_entry(APP_ID_KEY, **kwargs)

  def get_publisher_identifier(self, **kwargs) -> str:
    return self.read_typed_entry(publisher_identifier_key, **kwargs) or ''

  def get_app_identifier(self, **kwargs) -> str:
    return self.read_typed_entry(app_identifier_key, **kwargs) or ''

  def app_signature(self, **kwargs):
    return (
      self.get_app_identifier(**kwargs),
      self.get_publisher_identifier(**kwargs)
    )

  def get_install_id(self, **kwargs) -> str:
    return self.read_typed_entry(INSTALL_ID_KEY, **kwargs)

  def get_install_token(self, **kwargs) -> str:
    return self.read_typed_entry(INSTALL_TOKEN_KEY, **kwargs)

  def friendly_name(self, **kwargs) -> str:
    return self.read_typed_entry(friendly_name_key, **kwargs)

  def get_status(self, **kwargs) -> str:
    return self.read_typed_entry(STATUS_KEY, **kwargs)

  def prefs(self, **kwargs) -> Dict:  # TODO can we kill this crap?
    return self.read_typed_entry(prefs_config_key, **kwargs)

  def get_ktea_config(self, **kwargs) -> KteaDict:
    return self.read_typed_entry(KTEA_CONFIG_KEY, **kwargs)

  def get_kama_config(self, **kwargs) -> KamaDict:
    return self.read_typed_entry(KAMA_CONFIG_KEY, **kwargs) or {}

  def get_default_vars(self, **kwargs) -> Dict:
    return self.read_typed_entry(DEF_VARS_LVL, **kwargs) or {}

  def get_publisher_inj_vars(self, **kwargs) -> Dict:
    return self.read_typed_entry(VNDR_INJ_VARS_LVL, **kwargs) or {}

  def get_user_vars(self, **kwargs) -> Dict:
    return self.read_typed_entry(USER_VARS_LVL, **kwargs) or {}

  def last_updated(self, **kwargs) -> datetime:
    return self.read_typed_entry(LAST_UPDATED_KEY, **kwargs)

  def get_last_status_uploaded(self, **kwargs) -> datetime:
    return self.read_typed_entry(LAST_STATUS_UPLOAD_KEY, **kwargs)

  def get_merged_vars(self, **kwargs) -> Dict:
    return utils.deep_merge(
      self.get_default_vars(**kwargs),
      self.get_publisher_inj_vars(**kwargs),
      self.get_user_vars(**kwargs),
    )

  def read_var(self, deep_key: str, **kwargs) -> Optional[Any]:
    deep_vars = self.get_merged_vars(**kwargs)
    return utils.deep_get(deep_vars, deep_key)

  def last_injected(self, **kwargs) -> datetime:
    result = self.read_typed_entry(LAST_SYNCED_KEY, **kwargs)
    if result:
      return result
    else:
      use_backup = kwargs.pop('or_ancient', True)
      return helper.ancient_dt() if use_backup else None

  def unset_user_vars(self, var_keys: List[str], **kwargs):
    self.unset_deep_vars(USER_VARS_LVL, var_keys, **kwargs)

  def patch_user_vars(self, assignments: Dict[str, any], **kwargs):
    self.patch_into_deep_dict(USER_VARS_LVL, assignments, **kwargs)

  def patch_def_vars(self, assignments: Dict, **kwargs):
    self.patch_into_deep_dict(DEF_VARS_LVL, assignments, **kwargs)

  def patch_vnd_inj_vars(self, assignments: Dict[str, any], **kwargs):
    self.patch_into_deep_dict(VNDR_INJ_VARS_LVL, assignments, **kwargs)

  def patch_prefs(self, assignments: Dict[str, any], **kwargs):
    self.patch_into_deep_dict(prefs_config_key, assignments, **kwargs)

  def write_last_synced(self, timestamp: datetime, **kwargs):
    self.write_typed_entry(LAST_SYNCED_KEY, timestamp, **kwargs)

  def write_last_status_uploaded(self, timestamp: datetime, **kwargs):
    self.write_typed_entry(LAST_STATUS_UPLOAD_KEY, timestamp, **kwargs)

  def write_last_injected(self, timestamp: datetime, **kwargs):
    self.write_typed_entry(LAST_SYNCED_KEY, timestamp, **kwargs)

  def write_ktea(self, new_ktea: KteaDict, **kwargs):
    self.write_typed_entry(KTEA_CONFIG_KEY, new_ktea, **kwargs)

  def write_status(self, new_status: str, **kwargs):
    self.write_typed_entry(STATUS_KEY, new_status, **kwargs)

  def write_space_statuses(self, statuses: Dict):
    for space, status in statuses.items():
      self.write_last_synced(datetime.now(), space=space)
      self.write_status(status, space=space)

  def patch_ktea(self, partial_ktea: KteaDict, **kwargs):
    new_ktea = {**self.get_ktea_config(), **partial_ktea}
    self.write_ktea(new_ktea, **kwargs)

  def write_default_vars(self, assigns: Dict, **kwargs):
    self.write_typed_entry(DEF_VARS_LVL, assigns, **kwargs)

  def write_user_vars(self, assigns: Dict, **kwargs):
    self.write_typed_entry(USER_VARS_LVL, assigns, **kwargs)

  def is_training_mode(self) -> bool:
    raw_val = self.read_entry(IS_PROTOTYPE_KEY)
    return raw_val in ['True', 'true', True]

  def is_real_deployment(self) -> bool:
    if env_utils.is_test():
      return False
    else:
      return not self.is_training_mode()

  def merged_manifest_vars(self, **kwargs) -> Dict:
    return {
      **self.get_default_vars(**kwargs),
      **self.get_publisher_inj_vars(**kwargs),
      **self.get_user_vars(**kwargs)
    }

  def _log_if_nil_source_after_reload(self):
    if not self._cmap:
      cmap_id = f"[{self.get_ns()}/{KAMAFILE}]"
      msg = f"load_master_cmap {cmap_id} nil (tried reload)"
      lerr(msg, trace=True, sig="config_man")


config_man = ConfigMan()


def _read_ns() -> Optional[str]:
  """
  Reads application namespace from a file. If in-cluster, path
  will be Kubernetes default
  /var/run/secrets/kubernetes.io/serviceaccount/namespace. Else,
  wiz must be running in dev or training mode and tmp path will be used.
  @return: name of new namespace
  """
  if env_utils.is_in_cluster():
    _ns = read_file_ns(_ns_path)
  else:
    _ns = read_dev_file_ns()
  if not _ns:
    lerr("FATAL read failed")
  return _ns


def read_file_ns(path):
  try:
    with open(path, 'r') as file:
      if contents := file.read():
        return contents.strip()
      else:
        lwar(f"ns file empty ({path})")
      return None
  except FileNotFoundError:
    return None


def read_ns_mapping() -> Dict[str, str]:
  if contents := read_file_ns(_out_of_cluster_ns_map_path):
    try:
      return json.loads(contents)
    except JSONDecodeError:
      pass
  return {}


def ns_file_key() -> str:
  pathname = os.path.dirname(sys.argv[0])
  return os.path.abspath(pathname)


def read_dev_file_ns() -> Optional[str]:
  return read_ns_mapping().get(ns_file_key())


def coerce_ns(new_ns: str):
  """
  For out-of-cluster Dev mode only. Changes global ns variable
  to new val, and also writes new val to file so that other processes
  (e.g worker queues) use the same value.
  @param new_ns: name of new namespace
  """
  if env_utils.is_out_of_cluster():
    config_man._ns = new_ns
    mapping = read_ns_mapping()
    with open(_out_of_cluster_ns_map_path, 'w') as file:
      mapping[ns_file_key()] = new_ns
      file.write(json.dumps(mapping))
  else:
    lwar(f"illegal ns coerce!")


def type_serialize_entry(key: str, value: Any):
  if expected_type := schema.get(key):
    if helper.does_type_match(value, expected_type):
      serialized_value = helper.serialize_outbound(value, expected_type)
      return serialized_value
    else:
      reason = f"[{key}]={value} must be {expected_type} " \
               f"but was {type(value)}"
      raise RuntimeError(f"[kama_sdk:config_man] {reason}")
  else:
    raise RuntimeError(f"[kama_sdk:config_man] illegal key {key}")


SPACE_KW = 'space'
RELOAD_KWARG = 'reload'

spaces_key = 'spaces'

IS_PROTOTYPE_KEY = 'is_prototype'
APP_ID_KEY = 'app_id'
INSTALL_ID_KEY = 'install_id'
INSTALL_TOKEN_KEY = 'install_token'
STATUS_KEY = 'status'
KTEA_CONFIG_KEY = 'ktea'
KAMA_CONFIG_KEY = 'kama'

friendly_name_key = 'friendly_name'
publisher_identifier_key = 'publisher_identifier'
app_identifier_key = 'app_identifier'

DEF_VARS_LVL = 'default_vars'
VNDR_INJ_VARS_LVL = 'vendor_injection_vars'
USER_INJ_VARS_LVL = 'user_injection_vars'
USER_VARS_LVL = 'user_vars'

prefs_config_key = 'prefs'  # TODO can we raze this crap?

LAST_UPDATED_KEY = 'last_updated'
LAST_SYNCED_KEY = 'last_synced'
LAST_STATUS_UPLOAD_KEY = 'last_status_uploaded'
update_checked_at_key = 'update_checked_at'

_install_token_path = '/etc/sec/install_token'
_mounted_cmap_root_path = '/etc/master_config'
_ns_path = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
_out_of_cluster_ns_map_path = '/tmp/kama_sdk_machine_namespaces'
_iso8601_time_fmt = '%Y-%m-%d %H:%M:%S.%f'

schema = {
  DEF_VARS_LVL: dict,
  VNDR_INJ_VARS_LVL: dict,
  USER_VARS_LVL: dict,
  USER_INJ_VARS_LVL: dict,
  prefs_config_key: dict,
  KTEA_CONFIG_KEY: dict,
  KAMA_CONFIG_KEY: dict,

  LAST_UPDATED_KEY: datetime,
  LAST_SYNCED_KEY: datetime,
  LAST_STATUS_UPLOAD_KEY: datetime,
  update_checked_at_key: datetime,

  IS_PROTOTYPE_KEY: bool,

  APP_ID_KEY: str,
  INSTALL_ID_KEY: str,
  INSTALL_TOKEN_KEY: str,
  STATUS_KEY: str,
  friendly_name_key: str,
  publisher_identifier_key: str,
  app_identifier_key: str

}

backup_mappings = {
  dict: {},
  str: ''
}

MANIFEST_VAR_LEVEL_KEYS = [
  DEF_VARS_LVL,
  VNDR_INJ_VARS_LVL,
  USER_INJ_VARS_LVL,
  USER_VARS_LVL
]
