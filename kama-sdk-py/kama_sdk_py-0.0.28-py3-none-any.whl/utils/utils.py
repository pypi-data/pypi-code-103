import collections
import functools
import random
import re
import string
import subprocess
from datetime import datetime
from functools import reduce
from typing import Dict, List, Tuple, Optional, Any, Callable, TypeVar

from k8kat.res.base.kat_res import KatRes
from k8kat.utils.main.api_defs_man import api_defs_man

from kama_sdk.core.core.types import KAO, K8sResDict, K8sResSig

X = TypeVar('X')


def is_listy(value: Any) -> bool:
  return isinstance(value, list)


def dictlike(value: Any) -> bool:
  return isinstance(value, dict)


def relaxed_subdict(source: Dict, *keys: str) -> Dict:
  """
  Returns a new dict equal to the subset of the `source: Dict` containing
  only keys in the input keys. Keys not in `source` will result in assignments
  with a null value.
  """
  return {k: source.get(k) for k in keys}


def shell_exec(command: str) -> str:
  cmd_parts = command.split(" ")
  exec_result = subprocess.run(cmd_parts, stdout=subprocess.PIPE, check=False)
  return exec_result.stdout.decode('utf-8')


def subdict(source: Dict, *keys: str) -> Dict:
  """
  Returns a new `Dict` equal to the subset of the `source: Dict` containing
  only keys in the input keys. Keys not in `source` will not be carried over
  to the new `Dict`.
  """

  return {k: v for k, v in source.items() if k in keys}


def subdict_without(_dict: Dict, *keys: str) -> Dict:
  """
  Returns a new dict equal to the subset of the input dict containing
  only keys NOT in the input keys.
  """
  return {k: v for k, v in _dict.items() if k not in keys}


def flat2deep(flat_dict: Dict) -> Dict:
  """
  From a dict with 'flat' assignments like {'x.y': 'z'}, returns a new dict
  with deep assignments, e.g {'x': {'y': 'z'}}. Any deep assignments will
  copied over unchanged.
  """
  keyed_assigns = list(flat_dict.items())
  root = {}
  for keyed_assign in keyed_assigns:
    deep_key_as_list = keyed_assign[0].split('.')  # fully qualified hash key
    _deep_set(root, deep_key_as_list, keyed_assign[1])
  return root


def deep_merge(*dicts: Dict):
  """
  Performs a deep merge from left to right on the input dicts. Will
  NOT attempt to deepen flat dicts.
  """
  from k8kat.utils.main.utils import deep_merge as k8kat_deep_merge
  merged = {}
  for _dict in dicts:
    merged = k8kat_deep_merge(merged, _dict)
  return merged


def deep_unset(deep_dict: Dict, victim_keys: List[str]) -> Dict:
  """
  Returns a new dict equal to the input dict without any assignments
  for which the flat key is contained in the victim_keys.
  """
  flat_source = deep2flat(deep_dict)
  for victim_key in victim_keys:
    flat_source.pop(victim_key, None)
  return flat2deep(flat_source)


def deep_merge_flats(flat_dicts: List[Dict]):
  """
  Given a "flat" dict `flat_dict: Dict`, return the deep-merge
  over the dicts from left to right.
  :param flat_dicts:
  :return:
  """
  deep_dicts = list(map(flat2deep, flat_dicts))
  return deep_merge(*deep_dicts)


def dict2keyed(assigns: Dict) -> List[Tuple[str, any]]:
  """
  SHOULD DEPRECATE. Remnant from reptile brain. Used only to service
  `deep2flat`.
  :param assigns:
  :return:
  """
  list_keyed_dict = _dict2keyed([], assigns)
  cleaner = lambda t: (".".join(t[0]), t[1])
  return list(map(cleaner, list_keyed_dict))


def deep2flat(assigns) -> Dict:
  tuples = dict2keyed(assigns)
  return {t[0]: t[1] for t in tuples}


def _dict2keyed(parents, assigns: Dict) -> List[Tuple[List[str], any]]:
  result: List[Tuple[List[str], any]] = []

  for assign in assigns.items():
    key, value = assign
    if type(value) == dict:
      result = result + _dict2keyed(parents + [key], value)
    else:
      result.append((parents + [key], value))
  return result


def deep_get(deep_dict: Dict, deep_key: str) -> Any:
  """
  Returns the value in a deep dict indexed by a deep key.
  If deep_dict is {'x': {'y': 'z'}} and deep_key is 'x.y', the output
  is 'z'.
  """
  key_parts = [k for k in deep_key.split('.') if not k.strip() == '']

  if len(key_parts) > 0:
    return reduce(
      lambda d, key: d.get(key, None)
      if isinstance(d, dict)
      else None, key_parts, deep_dict
    )
  else:
    return deep_dict


def _deep_set(deep_dict: Dict, key_parts: List[str], value: any) -> None:
  """
  Reptile brain remnant. Marked for removal in debt doc.
  Look at `utils.deep_set` instead.
  :param deep_dict:
  :param key_parts:
  :param value:
  :return:
  """
  if len(key_parts) == 1:
    deep_dict[key_parts[0]] = value
  else:
    if not deep_dict.get(key_parts[0]):
      deep_dict[key_parts[0]] = dict()
    _deep_set(deep_dict[key_parts[0]], key_parts[1:], value)


def deep_set(host_dict: Dict, flat_key: str, value: Any):
  """
  Given a host dict `host_dict: Dict`, and a flat assignment
  made of a flat key `flat_key: str` (e.g "foo.bar.baz") and
  a value `value: Any`, deep-sets the assignment into the host dict.
  This is an **in place operation** that modifies the `host_dict`.
  If the
  :param host_dict: any Dict
  :param flat_key:
  :param value:
  """
  _deep_set(host_dict, flat_key.split("."), value)


def dupes(_list: List[X]) -> List[X]:
  """
  Given a list `_list: List`, return the duplicated elements,
  i.e that appear more than once according to `==`.
  :param _list: 
  :return: 
  """
  items = collections.Counter(_list).items()
  return [item for item, count in items if count > 1]


def pluck_or_getattr_deep(obj, attr):
  """
  Deep attribute supplier.
  """
  def _getattr(_obj, _attr):
    if type(_obj) == dict:
      return _obj[_attr]
    else:
      if hasattr(_obj, _attr):
        func_or_lit = getattr(_obj, _attr)
        return func_or_lit() if callable(func_or_lit) else func_or_lit
      elif hasattr(_obj, "get_attr"):
        func = getattr(_obj, "get_attr")
        return func(_attr)

  try:
    return functools.reduce(_getattr, [obj] + attr.split('.'))
  except AttributeError:
    return None


def any2bool(anything: Any) -> bool:
  if type(anything) == bool:
    return anything
  elif type(anything) == str:
    if anything in ['true', 'True', 'yes', 'positive']:
      return True
    elif anything in ['false', 'False', 'None', 'no', 'negative']:
      return False
    else:
      return bool(anything)
  else:
    return bool(anything)


def snake2camel(name):
  """
  Credit: https://stackoverflow.com/a/1176023/11913562
  :param name:
  :return:
  """
  return ''.join(word.title() for word in name.split('_'))


def camel2snake(name):
  """
  Credit: https://stackoverflow.com/a/1176023/11913562
  :param name:
  :return:
  """
  return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def selects_labels(selector: Dict, actual_labels: Dict):
  """
  Simple Kubernetes-style label matching. Should be deprecated
  in favor of the more general `structured_search`.
  :param selector:
  :param actual_labels:
  :return:
  """
  for key, value in selector.items():
    value_as_list = value if is_listy(value) else [value]
    if key not in actual_labels.keys():
      return False
    if actual_labels[key] not in value_as_list:
      return False
  return True


def rand_str(string_len=10):
  """
  For simple SDK uses only, NOT crypto safe.
  :param string_len:
  :return:
  """
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for _ in range(string_len))


def clean_log_lines(chunk) -> List[str]:
  """
  Basic string sanitization for a log: split, strip, return list.
  :param chunk:
  :return:
  """
  if type(chunk) == str:
    log_lines = chunk.split("\n")
    weeder = lambda line: not line.strip() == ''
    return list(filter(weeder, log_lines))
  elif type(chunk) == list:
    return chunk
  else:
    return []


def log2kao(log: str) -> Optional[KAO]:
  """
  Given `log`, a line of output from `kubectl apply -f <...>`, returned
  a structured `Dict` representation where `api_group`, `kind`, etc are
  indexed. Returns None if parsing fails.
  :param log:
  :return:
  """
  try:
    api = ''
    kind_and_name, verb = log.split(" ")
    kind, name = kind_and_name.split("/")
    if "." in kind:
      parts = kind.split(".")
      kind = parts[0]
      api = '.'.join(parts[1:])
    return KAO(
      api_group=api,
      kind=kind,
      name=name,
      verb=verb,
      error=None
    )
  except:
    return None


def group_agg(_list: List, func: Callable) -> Dict[str, List]:
  output = {}
  for item in _list:
    key = func(item)
    if not key in output.keys():
      output[key] = []
    output[key].append(item)
  return output


def kao2log(kao: KAO) -> str:
  """
  Used only to present data to the user; correctness does not affect
  caller. Given a KAO, try reconstructing the original `kubectl apply`
  log line.
  :param kao:
  :return:
  """
  group_and_kind = ''
  if kao.get('api_group'):
    group_and_kind = f"{kao.get('api_group')}."
  group_and_kind = f"{group_and_kind}{kao.get('kind')}"
  identity = f"{group_and_kind}/{kao.get('name')}"

  if not kao.get('error'):
    return f"{identity} {kao.get('verb')}"
  else:
    return f"{identity} {kao.get('error')}"


def are_res_same(r1: K8sResSig, r2: K8sResSig):
  """
  Given two Kubernetes resource signatures (`kind` and `name`)
  `r1` and `r2`, return True if each attribute, when normalized,
  are equal. For `kind`, normalization means pluralizing and
  down-casing, as per `k8kat`'s `api_defs_man.kind2plurname`.
  :param r1:
  :param r2:
  :return:
  """
  norm_kind = lambda kind: api_defs_man.kind2plurname(kind)
  kinds_eq = norm_kind(r1['kind']) == norm_kind(r2['kind'])
  names_eq = r1['name'] == r2['name']
  return kinds_eq and names_eq


def full_res2sig(res_dict: K8sResDict) -> K8sResSig:
  meta = res_dict.get('metadata') or {}
  return K8sResSig(
    kind=res_dict.get('kind'),
    name=meta.get('name')
  )


def logs2outkomes(logs: List[str]) -> List[KAO]:
  """
  Given a list line lines `logs: List[str]` from `kubectl apply`,
  return a mapping from each line to `log2kao`, which yields
  a structured representation (`KAO`) of the line's contents.
  :param logs:
  :return:
  """
  outcomes = list(map(log2kao, logs))
  return [o for o in outcomes if o is not None]


def flatten(nested_list: List[List]) -> List:
  """
  Max two dimensional.
  :param nested_list:
  :return:
  """
  return [item for sublist in nested_list for item in sublist]


def values_at(_dict: Dict, *keys: str) -> Tuple:
  """
  Implementation or Ruby's Hash#values_at. Returns new tuple
  containing values indexed by keys in input _keys.
  :param _dict: source dict
  :param keys: whitelist of keys
  :return:
  """
  return tuple([_dict.get(k) for k in keys])


def compact(_list: List[Optional[Any]]) -> List[Any]:
  """
  Implementation or Ruby's Enumerable#compact. Returns new list equal
  to input list minus any nullish values.
  Args:
    _list: input list potentially containing nullish values
  Returns: new list
  """
  return [item for item in _list if item is not None]


def unmuck_primitives(root: Any) -> Any:
  if type(root) == dict:
    return {k: unmuck_primitives(v) for k, v in root.items()}
  elif type(root) == list:
    return list(map(unmuck_primitives, root))
  else:
    return unmuck_primitive(root)


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


def unmuck_primitive(original: Any) -> Any:
  if type(original) == str:
    if original.isdigit():
      return int(original)
    elif isfloat(original):
      return float(original)
    elif original.lower() == 'true':
      return True
    elif original.lower() == 'false':
      return False
    else:
      return original
  else:
    return original


def kres2dict(kat_res: KatRes) -> Optional[Dict]:
  if kat_res:
    if raw_res := kat_res.raw:
      as_dict = raw_res.to_dict()
      as_dict['kind'] = kat_res.kind
      return sanitize_kres_values(as_dict)
    else:
      print("[kama_sdk:res_sup] danger kat_res has no .raw")
      print(kat_res)
      return sanitize_kres_values(kat_res.__dict__)
  else:
    return None


def safely(func: Callable, bkp=None) -> Any:
  """
  Convenience to avoid a multi-line `try/except` block that behaves
  trivially. Given a function pointer `func: Callable`, run the function
  and return its output, or None if the function raises.
  :param func:
  :param bkp:
  :return:
  """
  try:
    return func()
  except:
    return bkp


def cautiously(func: Callable, bkp=None) -> Tuple[Any, Optional[Exception]]:
  try:
    return func(), None
  except Exception as e:
    return bkp, e


def sanitize_kres_values(root: Any) -> Any:
  if dictlike(root):
    new_root = {}
    for key, value in root.items():
      if is_listy(value):
        new_root[key] = list(map(sanitize_kres_values, value))
      elif dictlike(value):
        new_root[key] = sanitize_kres_values(value)
      elif isinstance(value, datetime):
        new_root[key] = str(value)
      else:
        new_root[key] = value
    return new_root
  else:
    return root


def unique(_list: List, predicate=None) -> set:
  """
  Returns a new set equal to the input list without duplicates.
  Equality is computed with '==' or "if predicate(item)" if predicate
  is given.
  Args:
    _list: input list with potential duplicates
    predicate: optional equality checker
  """
  seen = set()
  seen_add = seen.add
  if predicate is None:
    for item in _list:
      if item not in seen:
        seen_add(item)
        yield item
  else:
    for item in _list:
      val = predicate(item)
      if val not in seen:
        seen_add(val)
        yield item
