import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Type, Any

from k8kat.res.config_map.kat_map import KatMap
from typing_extensions import TypedDict

from kama_sdk.core.core.consts import KAMAFILE
from kama_sdk.utils import utils
from kama_sdk.utils.logging import lwar

"""

"""


class CmapAccessRecord(TypedDict):
  read_ts: datetime
  write_ts: datetime


def serialize_outbound(value: Any, exp_type: Type) -> Any:
  if exp_type == bool:
    return utils.any2bool(value)
  elif exp_type == dict:
    return value
  elif exp_type == str:
    return value or ""
  elif exp_type == datetime:
    return value.strftime(iso8601_time_fmt)
  else:
    print(f"[kama_sdk:patch] bad type {exp_type} for {value}")
    return str(value)


def parse_inbound(raw_value: str, type_mapping: Type) -> Any:
  if type_mapping == bool:
    return utils.any2bool(raw_value)
  elif type_mapping == datetime:
    return parse_ts(raw_value)
  else:
    return raw_value


def parse_ts(raw_value, backup=None) -> Optional[datetime]:
  parsed = None
  if raw_value:
    try:
      parsed = datetime.strptime(raw_value, iso8601_time_fmt)
    except TypeError:
      pass
  return parsed or backup


def does_type_match(value: Any, expected: Type) -> bool:
  if expected == bool:
    strings = ['true', 'false', 'True', 'False']
    return value in [True, False, None,  *strings]
  else:
    return type(value) == expected


def track_cmap_read(ns: str):
  patch_tracker(ns, READ_TS_KEY)


def track_cmap_write(ns: str):
  patch_tracker(ns, WRITE_TS_KEY)


def patch_tracker(ns: str, key: str):
  # print(f"PATCH {key} {datetime.now()}")
  crt = read_tracker(ns)
  updated_tracker = {**crt, NS_KEY: ns, key: datetime.now()}
  with open(io_tracker_fname, 'w') as file:
    serialized = serialize_tracker(updated_tracker)
    file.write(json.dumps(serialized))


def serialize_tracker(tracker: CmapAccessRecord) -> Dict:
  return {
    **tracker,
    READ_TS_KEY: tracker[READ_TS_KEY].strftime(iso8601_time_fmt),
    WRITE_TS_KEY: tracker[WRITE_TS_KEY].strftime(iso8601_time_fmt)
  }


def is_cmap_dirty(ns: str):
  tracker = read_tracker(ns)
  return tracker[WRITE_TS_KEY] >= tracker[READ_TS_KEY]


def ancient_dt(offset=0) -> datetime:
  date_time_str = f'2000-01-01 0{offset}:00:00.000000'
  return datetime.strptime(date_time_str, iso8601_time_fmt)


def should_reload_cmap(cmap: KatMap, ns: str, strategy: Any) -> bool:
  if cmap:
    if strategy in [None, 'auto'] and is_cmap_dirty(ns):
      return True
    elif strategy is True:
      return True
    return False
  else:
    return True


def read_tracker(ns: str) -> CmapAccessRecord:
  Path(io_tracker_fname).touch(exist_ok=True)
  with open(io_tracker_fname, 'r+') as file:
    contents = file.read() or '{}'
    try:
      parsed = json.loads(contents)
      if not parsed.get(NS_KEY) == ns:
        parsed = {}
    except:
      parsed = {}
    return {
      NS_KEY: ns,
      READ_TS_KEY: parse_ts(parsed.get(READ_TS_KEY), ancient_dt(0)),
      WRITE_TS_KEY: parse_ts(parsed.get(WRITE_TS_KEY), ancient_dt(1))
    }


def do_load_cmap(namespace: str) -> Optional[KatMap]:
  tries = 0
  max_tries = 4
  while tries < max_tries:
    if cmap := KatMap.find(KAMAFILE, namespace):
      return cmap
    lwar(f"cmap read fail {tries}/{max_tries}")
    tries = tries + 1
  return None


def clear_trackers():
  if os.path.exists(io_tracker_fname):
    try:
      os.remove(io_tracker_fname)
    except FileNotFoundError:
      msg = f"race condition on {io_tracker_fname}"
      lwar(f"{msg}, process restart recommended")


NS_KEY = 'namespace'
READ_TS_KEY = 'read_ts'
WRITE_TS_KEY = 'write_ts'

iso8601_time_fmt = '%Y-%m-%d %H:%M:%S.%f'
io_tracker_fname = '/tmp/kama_io_tracker.json'
