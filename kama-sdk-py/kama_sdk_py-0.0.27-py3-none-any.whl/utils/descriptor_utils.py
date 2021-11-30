import os
from typing import List, Dict

import yaml
from os import listdir
from os.path import isfile, join, isdir
from yaml import scanner

from kama_sdk.model.base.mc import KIND_KEY, ID_KEY
from kama_sdk.utils import utils


def _is_file_yaml(path: str) -> bool:
  return isfile(path) and \
         (path.endswith(".yaml") or path.endswith(".yml"))


def load_dir_yamls(path: str, recursive=True) -> List[Dict]:
  """
  Given a root path `dir_path: str`, parse all YAML files inside
  and return flattened list where each item is a `---` demarcated
  item in the list. Searches recursively if `recursive: bool` is `True`.
  A YAML file must have a `.yaml` or `.yml` extension.
  :param path: absolute path of the directory in which to start searching
  :param recursive: 
  :return: 
  """
  fnames = [f for f in listdir(path) if _is_file_yaml(join(path, f))]
  yaml_arrays = [load_file_yamls(f"{path}/{fname}") for fname in fnames]
  if recursive:
    sub_dirs = [f for f in listdir(path) if isdir(join(path, f))]
    for sub_dir in sub_dirs:
      yaml_arrays.append(load_dir_yamls(join(path, sub_dir), True))
  return utils.flatten(yaml_arrays)


def load_file_yamls(fname) -> List[Dict]:
  """
  Converts a YAML file into a list of dicts.
  :param fname: YAML file.
  :return: list of dicts.
  """
  with open(fname, 'r') as stream:
    file_contents = stream.read()
    try:
      raw_list = list(yaml.full_load_all(file_contents))
      reject_nullish = lambda y: len((y or {}).items()) > 0
      return list(filter(reject_nullish, raw_list))
    except scanner.ScannerError as e:
      print(f"[kama_sdk::utils] YAML parse error @ {fname}")
      raise e


def debug_sig(descriptor: Dict) -> str:
  if descriptor:
    kind = descriptor.get(KIND_KEY) or "no_kind"
    _id = descriptor.get(ID_KEY) or "no_id"
    return f"{kind}/{_id}"
  else:
    return "undefined"


def load_sdk_defaults() -> List[Dict]:
  pwd = os.path.join(os.path.dirname(__file__))
  search_space_root = f"{pwd}/../descriptors"
  return load_dir_yamls(search_space_root, recursive=True)
