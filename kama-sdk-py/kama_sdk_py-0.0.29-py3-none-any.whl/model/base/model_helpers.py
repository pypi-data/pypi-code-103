from __future__ import annotations

from typing import Type, TypeVar, Any, Callable, Optional

from kama_sdk.core.core.types import KoD
from kama_sdk.model.base.mc import VirtualAttrEntry, KIND_KEY, LAZY_KEY
from kama_sdk.model.base.model_decorators import FUNCTION_ATTR_KEY, SHOULD_CACHE_KEY, CACHE_READER_KEY, CACHE_WRITER_KEY
from kama_sdk.utils.logging import lerr, lwar

T = TypeVar('T', bound='Model')
A = TypeVar('A')


def do_type_check(k: str, v: Any, exp: Type, sig: str, **kwargs) -> Any:
  if isinstance(v, exp):
    return v
  else:
    msg = f"expected {k} to be a(n) {exp.__name__}; " \
          f"instead was a(n) {type(v)} ({v})"

    if kwargs.get('raise'):
      raise RuntimeError(msg)
    else:
      if 'alt' in kwargs.keys():
        ret = kwargs.get('alt')
      else:
        ret = v
      lwar(msg, sig=sig)
      return ret


def typed(v: Any, exp: Type[A], backup: A) -> A:
  if isinstance(v, exp):
    return v
  else:
    return backup


def is_interceptor_candidate(interceptor: Optional[Type[T]], prefix, kod: KoD):
  if isinstance(kod, dict) and interceptor:
    if not kod.get(LAZY_KEY):
      interceptors = interceptor.lteq_classes()
      if kod.get(KIND_KEY) in [c.__name__ for c in interceptors]:
        return True
      else:
        return False
    else:
      return False
  if isinstance(kod, str):
    return kod.startswith(prefix)
  return False


def resolve_backup(**kwargs):
  lazy_backup = kwargs.pop('lazy_backup', None)
  if lazy_backup is not None:
    return True, lazy_backup()
  elif 'backup' in kwargs.keys():
    return True, kwargs.pop('backup', None)
  else:
    return False, None


def handle_lookup_failed(key, sig, **kwargs):
  if on_miss := kwargs.pop('missing', None):
    msg = f"required prop {key} not supplied"
    if on_miss == 'warn':
      lerr(msg, sig=sig)
    if on_miss == 'raise':
      raise RuntimeError(msg)
  return None


def func_to_virtual_attr_entry(name, func: Callable) -> VirtualAttrEntry:
  return VirtualAttrEntry(
    func_name=name,
    attr_name=getattr(func, FUNCTION_ATTR_KEY),
    should_cache=getattr(func, SHOULD_CACHE_KEY)
  )


def monkey_patch_func_for_patching(func: Callable):
  if getattr(func, SHOULD_CACHE_KEY):
    from kama_sdk.model.base.model import Model
    setattr(func, CACHE_READER_KEY, Model.get_invoked_func_cached_value)
    setattr(func, CACHE_WRITER_KEY, Model.cache_invoked_attr_func_result)
