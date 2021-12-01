import functools
from typing import Callable, Optional


def func2key(explicit_key: str, func: Callable) -> str:
  if explicit_key:
    return explicit_key
  else:
    func_name: str = func.__name__
    for prefix in FUNC_PREFIXES:
      if func_name.startswith(prefix):
        return f"{RESOLVED_PREFIX}{func_name[len(prefix):]}"
    return f"{RESOLVED_PREFIX}{func_name}"


def key2func(attr_name: str, func: Callable) -> Optional[str]:
  pass


def model_attr2(user_func=None, key: str = None, cached: bool = True):
  if not user_func:
    return functools.partial(model_attr, key=key, cached=cached)

  final_key = func2key(key, user_func)
  should_cache = cached

  # noinspection DuplicatedCode
  @functools.wraps(user_func)
  def new_func(*func_args, **func_kwargs):
    if should_cache:
      model_inst = func_args[0]
      cache_getter = getattr(new_func, CACHE_READER_KEY)
      cache_writer = getattr(new_func, CACHE_WRITER_KEY)
      handled, cached_value = cache_getter(model_inst, user_func.__name__)
      if handled:
        return cached_value
      else:
        ret = user_func(*func_args, **func_kwargs)
        cache_writer(model_inst, user_func.__name__, ret)
        return ret
    else:
      return user_func(*func_args, **func_kwargs)

  setattr(new_func, FUNCTION_ATTR_KEY, final_key)
  setattr(new_func, SHOULD_CACHE_KEY, should_cache)
  return new_func


def model_attr(key: str = None, cached: bool = False) -> Callable:
  def inner(user_func):
    should_cache = cached
    attr_key = func2key(key, user_func)

    # noinspection DuplicatedCode
    def new_func(*func_args, **func_kwargs):
      if should_cache:
        model_inst = func_args[0]
        cache_getter = getattr(new_func, CACHE_READER_KEY)
        cache_writer = getattr(new_func, CACHE_WRITER_KEY)
        handled, cached_value = cache_getter(model_inst, user_func.__name__)

        if handled:
          return cached_value
        else:
          ret = user_func(*func_args, **func_kwargs)
          cache_writer(model_inst, user_func.__name__, ret)
          return ret
      else:
        return user_func(*func_args, **func_kwargs)
    setattr(new_func, FUNCTION_ATTR_KEY, attr_key)
    setattr(new_func, SHOULD_CACHE_KEY, should_cache)
    return new_func

  # print(f"INNER ID {inner}")
  return inner


ATTR_KEY_KEY = 'key'
FUNCTION_ATTR_KEY = 'attr_key'
CACHING_API_KEY = 'cached'
SHOULD_CACHE_KEY = 'should_cache'
RESOLVED_PREFIX = 'resolved_'
FUNC_PREFIXES = ["get_", "compute_"]
CACHE_READER_KEY = 'cache_reader'
CACHE_WRITER_KEY = 'cache_writer'
