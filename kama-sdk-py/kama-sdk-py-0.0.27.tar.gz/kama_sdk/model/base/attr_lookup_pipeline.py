from __future__ import annotations

from typing import Tuple, List, Callable, Dict, Any, Optional

from typing_extensions import TypedDict

from kama_sdk.model.base import mc
from kama_sdk.model.base.mc import AttrLookupOpts, DEF_LOOKUP_OPTS, prefix_sugar_sugar_mappings
from kama_sdk.model.base.model import Model
from kama_sdk.utils import utils

"""
Module intended as a mixin for Model. Handles all logic for performing
non-trivial attribute lookup. 
"""

class AttrLookupReq(TypedDict):
  model: Model
  attr_key: str
  options: AttrLookupOpts


UnpackedReq = Tuple[Model, str, AttrLookupOpts]
Lookup = Tuple[bool, Any, Optional[Model]]


def get_handlers() -> List[Callable[[AttrLookupReq], Lookup]]:
  return [
    try_preempt_with_cache,
    try_preempt_with_descriptor_override,
    try_preempt_with_virtual_override,
    try_standard_lookup,
    try_fallback_cache_spec_lookup,
    try_fallback_parent_lookup,
  ]


def process(req: AttrLookupReq) -> Lookup:
  final_req = pre_process_req(req)

  for handler_func in get_handlers():
    handled, value, delgate = handler_func(final_req)
    if handled:
      return True, value, delgate

  return False, None, None


def pre_process_req(req: AttrLookupReq) -> AttrLookupReq:
  """
  Returns new request with keys de-sugared and options merged with
  default.
  :param req: original request
  :return: new request ready for processing
  """
  model, key, options = unpack_req(req)
  sugar_free_key, implied_opts = sugar2options(key)
  final_opts = utils.deep_merge(DEF_LOOKUP_OPTS, implied_opts, options)
  return AttrLookupReq(
    model=model,
    attr_key=sugar_free_key,
    options=final_opts
  )


def sugar2options(raw_key: str) -> Tuple[str, Dict]:
  """
  For a raw_key, if it starts with a sugar prefix, returns tuple of
  the sugar-free key and the pipeline options the sugar prefixed demanded.
  If raw_key is sugar-free, returns the original raw_key and an empty dict
  :param raw_key:
  :return:
  """
  for sugar_option_mapping in prefix_sugar_sugar_mappings:
    prefix = sugar_option_mapping['prefix']
    if raw_key.startswith(prefix):
      options = sugar_option_mapping['options']
      sugarless_key = raw_key[len(prefix):]
      return sugarless_key, options
  return raw_key, {}


def unpack_req(req: AttrLookupReq) -> UnpackedReq:
  """
  Convenience method for handlers to inline args
  :param req:
  :return:
  """
  return req['model'], req['attr_key'], req['options']


def try_preempt_with_virtual_override(request: AttrLookupReq) -> Lookup:
  """
  If options permit and model has an instance method bound
  to this attr key, return the result of that method.
  :param request:
  :return:
  """
  model, key, options = unpack_req(request)
  if options['virtual']:
    if key in model.get_virtual_attr_names():
      return True, model.invoke_virtual_attr_func(key), model
  return False, None, None


def try_preempt_with_cache(request: AttrLookupReq) -> Lookup:
  """
  If options permit and key is in cache spec, return
  key-index value in the cache.
  :param request:
  :return:
  """
  model, key, options = unpack_req(request)
  if options['cache']:
    if key in model.get_results_cache().keys():
      return True, model.get_results_cache()[key], model
  return False, None, None


def try_preempt_with_descriptor_override(request: AttrLookupReq) -> Lookup:
  """
  Given a normal key like 'title', check if the descriptor has an
  override, e.g '_override_title' and if so return that value instead.
  """
  model, key, options = unpack_req(request)
  if options['redefine']:
    if key in model.get_redefinitions_spec().keys():
      return True, model.get_redefinitions_spec()[key], model
  return False, None, None


def prefix_key_with_override(attr_key: str) -> str:
  return f"{mc.NEW_ATTR_PREFIX}{attr_key}"


def try_standard_lookup(request: AttrLookupReq) -> Lookup:
  model, key, options = unpack_req(request)
  if options['standard']:
    descriptor = model.get_config()
    if key in descriptor.keys():
      return True, descriptor[key], model
  return False, None, None


def try_fallback_cache_spec_lookup(request: AttrLookupReq) -> Lookup:
  """
  Not to be confused with cache preempt. This is a fallback lookup.
  :param request:
  :return:
  """
  model, key, options = unpack_req(request)
  cache_spec = model.get_cache_spec()
  if key in cache_spec.keys():
    return True, cache_spec[key], model
  return False, None, None


def try_fallback_parent_lookup(request: AttrLookupReq) -> Lookup:
  model, key, options = unpack_req(request)
  if options['lookback']:
    if parent := request['model'].get_parent():
      new_req = AttrLookupReq(options={}, model=parent, attr_key=key)
      parent_lookup = process(new_req)
      return parent_lookup
  return False, None, None


# def try_cached_lookup(req: LookPipelineReq) -> LookupHandling:
#   model, key, options = unpack_req(req)


handlers: List[Callable[[AttrLookupReq], Lookup]] = [
  try_preempt_with_cache,
  try_preempt_with_descriptor_override,
  try_standard_lookup
]
