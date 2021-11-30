import os
from typing import List

from kama_sdk.model.base import mc


def load_sdk_defaults() -> List[str]:
  pwd = os.path.join(os.path.dirname(__file__))
  return [f"{pwd}/../../assets"]


def read_from_asset(given_name: str) -> str:
  _, path = given_name.split("::")
  from kama_sdk.model.base.models_manager import models_manager
  for dirpath in models_manager.asset_dir_paths():
    full_path = f"{dirpath}/{path}"
    if os.path.isfile(full_path):
      with open(full_path) as file:
        return file.read()
  return ''


def try_read_from_asset(name: str):
  if name and type(name) == str:
    if name.startswith(mc.ASSETS_PREFIX):
      return read_from_asset(name)
  return name
