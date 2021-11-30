import base64
import json
from typing import Dict, Optional

from flask import request

from kama_sdk.core.core import consts
from kama_sdk.core.core.types import KoD
from kama_sdk.model.base.mc import SPACE_KEY
from kama_sdk.utils import utils


def std_parse():
  return request.json

def json_loads_parse():
  return json.loads(request.data)

def uni_esc_parse():
  payload_str = request.data.decode('unicode-escape')
  return json.loads(payload_str)

def uni_esc_trunc_parse():
  payload_str = request.data.decode('unicode-escape')
  truncated = payload_str[1:len(payload_str) - 1]
  return json.loads(truncated)

def parse_json_body() -> Dict:
  parsers = [std_parse, json_loads_parse, uni_esc_parse, uni_esc_trunc_parse]
  for parser in parsers:
    try:
      as_dict = parser()
      return utils.unmuck_primitives(as_dict)
    except:
      pass
  return {}

def debug_parse_json_body() -> Dict:
  results = {}
  parsers = [std_parse, json_loads_parse, uni_esc_parse, uni_esc_trunc_parse]
  for parser in parsers:
    try:
      results[parser.__name__] = parser()
    except Exception as e:
      results[parser.__name__] = str(e)
  return results


def space_id(force_single: bool, bkp_is_app=False):
  if value := request.args.get('space'):
    csv = list(map(str.strip, value.split(",")))
    return csv[0] if force_single else csv
  else:
    return consts.APP_SPACE_ID if bkp_is_app else None


def space_selector(force_single: bool, bkp_is_app=False):
  if space_or_spaces := space_id(force_single, bkp_is_app):
    return {SPACE_KEY: space_or_spaces}
  else:
    return {}


def id_param_to_kod(id_param: str) -> Optional[KoD]:
  try:
    utf_action_kod = base64.b64decode(id_param)
    try:
      return json.loads(utf_action_kod)
    except:
      return id_param
  except:
    return id_param
