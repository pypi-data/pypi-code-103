from __future__ import annotations

import inspect
from copy import deepcopy
from functools import lru_cache
from typing import Type, Optional, Dict, Union, List, TypeVar, Any

import yaml
# noinspection PyUnresolvedReferences
from typing_extensions import TypedDict

from kama_sdk.core.core import consts, str_sub
from kama_sdk.core.core.types import KoD, Handling
from kama_sdk.model.base import mc, model_helpers as helper
from kama_sdk.model.base import model_decorators as decor
from kama_sdk.model.base.exceptions import InflateError
from kama_sdk.model.base.mc import VirtualAttrEntry, KIND_KEY, ID_KEY, KIND_REFERENCE_PREFIX, EXPR_REFERENCE_PREFIX, \
  ID_REFERENCE_PREFIX, PATCH_KEY, INHERIT_KEY, WEAK_PATCH_KEY, FORCE_INFLATE_PREFIX, KOD_KW, INFLATE_SAFELY_KW
from kama_sdk.model.base.model_decorators import SHOULD_CACHE_KEY
from kama_sdk.model.base.model_helpers import func_to_virtual_attr_entry, typed
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.model.supplier.base.expr2config import expr2config
from kama_sdk.utils import utils, asset_utils
from kama_sdk.utils.logging import lerr, lwar

T = TypeVar('T', bound='Model')
CT = TypeVar('CT', bound='Model')


class Model:

  _config: Dict[str, Any]
  _parent: Optional['Model']
  _cache: Dict

  def __init__(self, config: Dict):
    self.tag_funcs()
    self._config = deepcopy(config)
    self._parent = None
    self._config[KIND_KEY] = self.__class__.__name__
    self._cache = {}

  def get_config(self) -> Dict:
    return self._config

  def get_id(self) -> str:
    return self.get_config().get(ID_KEY)

  def get_kind(self) -> str:
    return self.get_config().get(KIND_KEY)

  def sig(self) -> str:
    """
    Returns developer-readble identifier for the instance. For debug/telem.
    Returns:
      object:
    """
    safe_id = self.get_config().get(ID_KEY)
    return f"{self.get_kind()}/{safe_id}"

  def get_parent(self) -> Optional['Model']:
    return self._parent

  def find_nth_parent(self, n: int) -> 'Model':
    """
    Follows the parent chain backwards, returning the nth parent (self being 0)
    Args:
      n: distance to self

    Returns: Model subclass instance

    """
    if n == 0:
      return self
    else:
      return self._parent.find_nth_parent(n - 1) if self._parent else None

  def find_parent_by_type(self, cls_type: Type['Model']) -> 'Model':
    """
    Returns the **first** parent instance to be an instance of the
    given `cls_type`.
    :param cls_type:
    :return:
    """
    if isinstance(self, cls_type):
      return self
    else:
      return self.find_parent_by_type(cls_type)

  def set_parent(self, parent: 'Model'):
    self._parent = parent

  def get_title(self) -> Optional[str]:
    return self.get_local_attr(mc.TITLE_KEY, lookback=False)

  def get_info(self) -> Optional[str]:
    return self.get_local_attr(mc.INFO_KEY, lookback=False)

  def get_synopsis(self) -> str:
    return self.get_local_attr(mc.SYNOPSIS_KEY, lookback=False)

  def get_tags(self) -> List[str]:
    return self.get_attr(mc.TAGS_KEY, lookback=False, backup=[])

  def get_labels(self) -> Dict:
    value = self.get_local_attr(mc.LABELS_KEY, lookback=False) or {}
    return self.type_check(mc.LABELS_KEY, value, Dict, alt={})

  def get_space_id(self):
    return self.get_attr(mc.SPACE_KEY)

  def get_config_space(self) -> str:
    # ideally safe to return None though
    if explicit := self.get_attr(mc.CONFIG_SPACE_KEY, lookback=True):
      value = explicit
    else:
      value = self.get_space_id()
    return value or consts.APP_SPACE_ID

  def to_dict(self):
    return dict(
      id=self.get_id(),
      title=self.get_title(),
      info=self.get_info()
    )

  @lru_cache
  def get_virtual_attr_names(self) -> List[str]:
    return [e['attr_name'] for e in self.get_virtual_attr_defs()]

  @lru_cache(4)
  def find_attr_from_func(self, func_name: str) -> Optional[VirtualAttrEntry]:
    def find(entry: VirtualAttrEntry):
      return entry['func_name'] == func_name
    return next(filter(find, self.get_virtual_attr_defs()), None)

  @lru_cache(4)
  def find_func_from_attr(self, attr_name: str) -> Optional[VirtualAttrEntry]:
    def find(entry: VirtualAttrEntry):
      return entry['attr_name'] == attr_name
    return next(filter(find, self.get_virtual_attr_defs()), None)

  @lru_cache
  def get_virtual_attr_defs(self) -> List[VirtualAttrEntry]:
    result = []
    for method_name, _ in inspect.getmembers(self.__class__):
      func = getattr(self.__class__, method_name)
      if hasattr(func, decor.FUNCTION_ATTR_KEY):
        result.append(func_to_virtual_attr_entry(method_name, func))
    return result

  def tag_funcs(self):
    for method_name, _ in inspect.getmembers(self.__class__):
      func = getattr(self.__class__, method_name)
      if hasattr(func, decor.FUNCTION_ATTR_KEY):
        helper.monkey_patch_func_for_patching(func)

  def cache_invoked_attr_func_result(self, func_name: str, value: Any):
    """
    Cache writer used when an instance method that that identifies as a
    `model_attr` returns its result. It would be better to funnel such
    calls through the normal `get_attr` pipeline, but until then, we need
    a special handler that can convert the instance method's name to
    an attribute name.
    :param func_name:
    :param value:
    :return:
    """
    if entry := self.find_attr_from_func(func_name):
      self.cache_attr_resolution_result(entry['attr_name'], value)
    else:
      message = f"{func_name} had no virtual attr entry!"
      lerr(message, trace=True, sig=self.sig())

  def get_invoked_func_cached_value(self, func_name: str) -> Handling:
    if entry := self.find_attr_from_func(func_name):
      attr_name = entry['attr_name']
      if attr_name in self._cache.keys():
        return True, self._cache[attr_name]
      else:
        return False, None
    else:
      lerr(f"{func_name} had no virtual attr entry!")
      print(self.get_virtual_attr_defs())
      return False, None

  def is_selectable_by(self, selector: Dict) -> bool:
    return utils.selects_labels(selector, self.get_labels())

  def update_attrs(self, config: Dict):
    for key, value in config.items():
      setattr(self, key, value)

  def get_attr(self, key: str, **kwargs) -> Any:
    """
    Given an attribute name (key), gets the value from the descriptor
    (via lookup_attr) and applies transform if value demands it
    (via resolve_attr_value). Falls back to special behavior if the
    key was not found (via resolve_backup).
    :param key: actual key or sugar-coated key (see attr_lookup_pipeline)
    :param kwargs:
    :return: value
    """
    was_handled, raw_val, delegate = self.lookup_attr(key, **kwargs)
    if was_handled:
      resolved_val = delegate.resolve_attr_value(raw_val, **kwargs)
      delegate.cache_attr_resolution_result(key, resolved_val)
      return resolved_val
    else:
      backup_handled, backup_value = helper.resolve_backup(**kwargs)
      if backup_handled:
        return backup_value
      else:
        return helper.handle_lookup_failed(key, self.sig())

  def get_local_attr(self, key: str, **kwargs) -> Any:
    """
    Convenience for calling get_attr with lookback=False, which is a common
    use case.
    :rtype: object
    """
    new_kwargs = {**kwargs, mc.PARENT_LOOKBACK_ENABLED_FLAG: False}
    return self.get_attr(key, **new_kwargs)

  def lookup_attr(self, key: str, **kwargs):
    from kama_sdk.model.base import attr_lookup_pipeline as pipeline
    from kama_sdk.model.base.attr_lookup_pipeline import AttrLookupReq
    options = utils.subdict(kwargs, *mc.LOOKUP_OPT_KEYS)
    request = AttrLookupReq(model=self, attr_key=key, options=options)
    result = pipeline.process(request)
    return result

  def resolve_attr_value(self, value: Any, **kwargs) -> Optional[Any]:
    if isinstance(value, str):
      return self.resolve_str_attr_value(value)
    elif isinstance(value, list):
      return self.resolve_list_attr_value(value, **kwargs)
    elif isinstance(value, dict):
      return self.resolve_dict_attr_value(value, **kwargs)
    else:
      return value

  def cache_attr_resolution_result(self, key: str, result: Any):
    if key in self.get_cacheable_attr_keys():
      self._cache[key] = result

  def get_typed_attr(self, key: str, exp: Type, **kwargs) -> Any:
    value = self.get_attr(key)
    return self.type_check(key, value, exp, **kwargs)

  def type_check(self, key: str, value: Any, exp: Type, **kwargs) -> Any:
    sanitized = helper.do_type_check(key, value, exp, self.sig(), **kwargs)
    if not value or not value == sanitized:
      if kwargs.pop('patch', None):
        self.get_config()[key] = sanitized
    return sanitized

  def get_results_cache(self):
    return self._cache

  def clear_cached_results(self):
    self.get_results_cache().clear()

  def get_cache_spec(self) -> Dict:
    # kwargs = {'lookup_opts': {'parents': False}}
    # value = self.get_attr(mc.CACHE_SPEC_KEY, **kwargs) #TODO when below works
    value = self.get_config().get(mc.CACHE_SPEC_KEY) or {}
    return self.type_check(mc.CACHE_SPEC_KEY, value, Dict, alt={})

  def get_redefinitions_spec(self) -> Dict:
    value = self._config.get(mc.RE_DEFS_SPEC_KEY) or {}
    return self.type_check(mc.RE_DEFS_SPEC_KEY, value, Dict, alt={})

  @lru_cache
  def get_cacheable_attr_keys(self) -> List[str]:
    """
    Returns the list of attribute names that for which the caching
    mechanism should kick in. These come from two sources: 1) All keys
    from attributes inside the `cached` attributes, and 2) All instance
    methods with `@model_attr` decorators where `cached=True`.
    :return: list of keys
    """
    disc = lambda e: e[SHOULD_CACHE_KEY]
    entries = list(filter(disc, self.get_virtual_attr_defs()))
    pt1 = [e['attr_name'] for e in entries]
    return [*pt1, *self.get_cache_spec().keys()]

  def invoke_virtual_attr_func(self, attr_key: str) -> Optional[Any]:
    if entry := self.find_func_from_attr(attr_key):
      func = getattr(self.__class__, entry['func_name'])
      return func(self)
    else:
      lwar(f"illegal access attempt {attr_key}", sig=self.sig())

  def resolve_str_attr_value(self, value: Any):
    """
    For a given string, checks if it is eligible for a special resolution,
    and if so, applies the transformation. If more than one applies,
    the transformations are chained together in the following
    order:
    1. Supplier computation (e.g get::)
    2. String interpolation (e.g "${get::}")
    3. Asset resolution (e.g assets::)
    :param value: potentially resolvable value
    :return:
    """
    if value in mc.NULLISH_ALIASES:
      return None
    else:
      value = self.interpolate_str_attr_value(value)
      value = self.supplier_resolve_or_identity(value)
      value = self.inflation_resolve_or_identity(value)
      value = asset_utils.try_read_from_asset(value)
      return value

  def resolve_list_attr_value(self, value: List, **kwargs):
    """
    For each item in the given list, send it through the
    special resolution pipeline. If an item is a KOD that resolves
    to a list, and if that item was prefixed by "...", then
    the list it resolved to will be flattened into the final output,
    instead of it being inserted as a single item (e.g nested).
    :param value: list of potentinally resolvable values
    :param kwargs:
    :return:
    """
    resolved_items = []
    for item in value:
      splatter_handled, splattered_items = self.handle_splatter(item, **kwargs)
      if splatter_handled:
        resolved_items.extend(splattered_items)
      else:
        resolved_item = self.resolve_attr_value(item, **kwargs)
        resolved_items.append(resolved_item)
    return resolved_items

  def handle_splatter(self, item: Any, **kwargs) -> Handling:
    """
    Given a potential KOD item, if the item is a KOD that resolves
    to a list, and if that item was prefixed by "...", then
    the list it resolved to will be flattened into the final output,
    instead of it being inserted as a single item (e.g nested).
    :param item:
    :param kwargs:
    :return:
    """
    if isinstance(item, str) and item.startswith(mc.SPLATTER_PREFIX):
      resolvable_part = item[len(mc.SPLATTER_PREFIX):]
      resolved_item = self.resolve_attr_value(resolvable_part, **kwargs)
      if isinstance(resolved_item, list):
        return True, resolved_item
      elif resolved_item is not None:
        cause = f"{type(resolved_item)} {resolved_item}"
        lwar(f"cannot splatter non-list item {cause}", sig=self.sig())
        return True, []
    else:
      return False, None

  def resolve_dict_attr_value(self, value: Dict, **kwargs):
    depth = int(kwargs.get(mc.DEPTH_KW, mc.DEFAULT_DEPTH))
    txd_value = self.supplier_resolve_or_identity(value)
    if isinstance(txd_value, dict) and int(depth) > 0:
      sub_kwargs = {mc.DEPTH_KW: depth - 1}
      perf = lambda v: self.resolve_attr_value(v, **sub_kwargs)
      return {k: perf(v) for (k, v) in txd_value.items()}
    else:
      return txd_value

  def interpolate_str_attr_value(self, value: str) -> Any:
    """
    Performs string substitutions on input. Combines substitution context
    from instance's self.context and any additional context passed as
    parameters. Returns unchanged input if property is not a string.
    @param value: value of property to interpolate
    @return: interpolated string if input is string else unchanged input
    """
    if value and type(value) == str:
      def resolve(expr: str):
        ret = self.supplier_resolve_or_identity(expr)
        return str(ret) if ret else ''
      return str_sub.interpolate(value, resolve)
    else:
      return value

  @classmethod
  def kind(cls):
    return cls.__name__

  def serialize(self) -> Dict[str, Any]:
    src_items = list(self._config.items())
    no_copy = ['cache']
    return {k: v for k, v in src_items if k not in no_copy}

  def clone(self) -> T:
    new_model = self.__class__(self.serialize())
    new_model._parent = self._parent
    return new_model

  def inflate_children(self, child_cls: Type[CT], **kwargs) -> List[CT]:
    """
    Bottleneck function for a parent model to inflate a list of children.
    In the normal case, kods_or_provider_kod is a list of WizModels KoDs.
    In the special case, kods_or_provider_kod is ListGetter model
    that produces the actual children.
    case,
    @param child_cls: class all children must a subclass of
    @return: resolved list of WizModel children
    """
    kods_or_supplier = self.resolve_child_ref_kod(**{
      mc.ATTR_KW: kwargs.pop(mc.ATTR_KW, None),
      mc.KOD_KW: kwargs.pop(mc.KOD_KW, None)
    }) or []

    kod2child = lambda obj: self._kod2child(obj, child_cls, **kwargs)

    if utils.is_listy(kods_or_supplier):
      children_kods: List[KoD] = kods_or_supplier
      return list(map(kod2child, children_kods))
    elif type(kods_or_supplier) in [str, dict]:
      supplier_kod = kods_or_supplier
      from kama_sdk.model.supplier.base.supplier import Supplier

      children_kods = self.supplier_resolve_or_identity(supplier_kod)
      if isinstance(children_kods, list):
        return list(map(kod2child, children_kods))
      elif isinstance(children_kods, dict):
        query_dict = children_kods
        child_instances = child_cls.inflate_all(**{
          mc.QUERY_KW: query_dict
        })
        [c.set_parent(self) for c in child_instances]
        return child_instances
      else:
        err = f"children must be list or supplier not {supplier_kod}"
        raise RuntimeError(f"[Model] {err}")

  def inflate_child(self, child_cls: Type[CT], **kwargs) -> Optional[CT]:
    child_kod: KoD = self.resolve_child_ref_kod(**{
      mc.ATTR_KW: kwargs.pop(mc.ATTR_KW, None),
      mc.KOD_KW: kwargs.pop(mc.KOD_KW, None)
    })
    return self._kod2child(child_kod, child_cls, **kwargs)

  def resolve_child_ref_kod(self, **kwargs) -> Union[List[KoD], KoD]:
    if explicit_kod := kwargs.get(mc.KOD_KW):
      return explicit_kod
    elif attr_name := kwargs.get(mc.ATTR_KW):
      return self.get_attr(attr_name, )
    else:
      base = f"child ref from {self.sig()} must include kod or prop"
      lerr(f"{base} , neither found in {kwargs}", sig=self.sig())

  def _kod2child(self, kod: KoD, child_cls: Type[T], **kwargs) -> T:
    try:
      down_kw = {**kwargs, 'mute': False}
      inflated = child_cls.inflate(kod, **down_kw)
      if inflated:
        inflated._parent = self
      return inflated
    except Exception as e:
      exp_child_kind = child_cls.__name__ if isinstance(child_cls, type) else '?'
      child_part = f"child \"{kod}\":{exp_child_kind}"
      lerr(f"failed to inflate {child_part}", sig=self.sig())
      raise e

  def prop_inheritance_pool(self):
    return self._config

  def inflation_resolve_or_identity(self, kod: KoD) -> Any:
    prefix: str = FORCE_INFLATE_PREFIX
    if helper.is_interceptor_candidate(None, prefix, kod):
      final_kod = expr2config(kod[len(prefix):])
      down_kwargs = {KOD_KW: final_kod, INFLATE_SAFELY_KW: True}
      return self.inflate_child(Model, **down_kwargs)
    else:
      return kod

  def supplier_resolve_or_identity(self, kod: KoD) -> Any:
    from kama_sdk.model.supplier.base.supplier import Supplier
    prefix: str = mc.SUPPLIER_RESOLVE_PREFIX

    if helper.is_interceptor_candidate(Supplier, prefix, kod):
      final_kod = kod
      if isinstance(kod, str):
        final_kod = expr2config(kod[len(prefix):])
      elif not isinstance(kod, dict):
        lwar(f"kod type({type(kod)}) is not a KOD", sig=self.sig())

      down_kwargs = {KOD_KW: final_kod, INFLATE_SAFELY_KW: True}

      if interceptor := self.inflate_child(Supplier, **down_kwargs):
        resolved_value = interceptor.resolve()
        return resolved_value
    else:
      return kod

  def patch(self, new_props: Dict[str, any], invalidate=True) -> T:
    self._config = {**self._config, **new_props}
    if invalidate:
      self.get_results_cache().clear()
      pass
      # TODO replace!
      # for key in self.config.keys():
      #   if key in self.__dict__:
      #     invalidate_cached_property(self, key)
    return self

  @classmethod
  def inflate_single(cls: Type[T], **kwargs) -> Optional[Model]:
    models = cls.inflate_all(**kwargs)
    if (count := len(models)) > 1:
      sel_part = f"(sel={kwargs.get(mc.QUERY_KW)})"
      lwar(f"expected 1 result, got {count} {sel_part}", sig=cls.__name__)
    return models[0] if len(models) > 0 else None

  @classmethod
  def query(cls: Type[T], query: Dict) -> List[T]:
    return cls.inflate_all(q=query)

  @classmethod
  def inflate_all(cls: Type[T], **kwargs) -> List[T]:
    query_expr = kwargs.pop(mc.QUERY_KW, None)
    cls_pool = cls.lteq_classes()
    config_pool = models_manager.query_descriptors(query_expr)
    config_pool = models_manager.configs_for_classes(config_pool, cls_pool)
    return [cls.inflate(config, **kwargs) for config in config_pool]

  @classmethod
  def inflate_many(cls: Type[T], kods: List[KoD], **kwargs) -> List[Model]:
    instances: List[Model] = []
    safely = kwargs.pop(mc.INFLATE_SAFELY_KW, False)
    for kod in kods:
      try:
        instances.append(cls.inflate(kod, **kwargs))
      except Exception as e:
        if not safely:
          raise e
    return instances

  @classmethod
  def inflate(cls: Type[T], kod: KoD, **kwargs) -> Optional[T]:
    try:
      if isinstance(kod, str):
        return cls.inflate_with_str(kod, **kwargs)
      elif isinstance(kod, Dict):
        return cls.inflate_with_config(kod, **kwargs)
      else:
        raise InflateError(f"inflate value {kod} neither dict or str")
    except Exception as err:
      if kwargs.pop(mc.INFLATE_SAFELY_KW, False):
        return None
      else:
        if not kwargs.pop('mute', False):
          lerr(f"inflate error below for {kod}", sig=cls.csig())
        raise err

  @classmethod
  def csig(cls) -> str:
    """
    Short for 'class signature'. We bother having a  method for this
    simple of logic in case we want to change the behavior for
    all Models at some point.
    :return:
    """
    return cls.__name__

  @classmethod
  def from_yaml(cls: Type[T], yaml_str: str, **kwargs) -> Optional[T]:
    as_dict = yaml.load(yaml_str)
    return cls.inflate_with_config(as_dict, **kwargs)

  @classmethod
  def inflate_with_str(cls: Type[T], ref_or_expr: str, **kwargs) -> T:
    """
    Given a superclass to bound the search space, and a descriptor
    id/kind/sugar-expr, queries registered descriptors, and if one
    is found, returns a model inflated with it.
    :param ref_or_expr: an id::<x>, kind::<x>, or expr<x>
    :param kwargs:
    :return: instance of T
    """
    if ref_or_expr.startswith(KIND_REFERENCE_PREFIX):
      referenced_kind = ref_or_expr.split(KIND_REFERENCE_PREFIX)[1]
      return cls.inflate_with_kind_reference(referenced_kind, **kwargs)

    elif ref_or_expr.startswith(ID_REFERENCE_PREFIX):
      referenced_id = ref_or_expr.split(mc.ID_REFERENCE_PREFIX)[1]
      return cls.inflate_with_id_reference(referenced_id, **kwargs)

    elif ref_or_expr.startswith(EXPR_REFERENCE_PREFIX):
      literal_expr = ref_or_expr.split(mc.EXPR_REFERENCE_PREFIX)[1]
      return cls.inflate_with_literal(literal_expr, **kwargs)

    else:
      return cls.inflate_with_id_reference(ref_or_expr, **kwargs)

  @classmethod
  def inflate_with_literal(cls: Type[T], expr: str, **kwargs) -> Optional[T]:
    return None

  @classmethod
  def inflate_with_kind_reference(cls: Type[T], kind_ref: str, **kwargs) -> T:
    config = dict(kind=kind_ref)
    return cls.inflate_with_config(config, **kwargs)

  @classmethod
  def inflate_with_id_reference(cls: Type[T], id_ref: str, **kwargs) -> T:
    query_expr = kwargs.pop(mc.QUERY_KW, None)
    config = models_manager.find_desc_in_subtree(id_ref, cls, query_expr)
    return cls.inflate_with_config(config, **kwargs)

  @classmethod
  def descendent_or_self(cls: Type[T]) -> Type[T]:
    subclasses = cls.lteq_classes(models_manager.get_model_classes())
    not_self = lambda kls: not kls == cls
    return next(filter(not_self, subclasses), cls)({})

  @classmethod
  def inflate_with_config(cls: Type[T], descriptor: Dict, **kwargs) -> T:

    if descriptor is None:
      raise InflateError("inflate_with_config given no config")

    raw_weak_patch = kwargs.get(WEAK_PATCH_KEY)
    raw_strong_patch = kwargs.get(PATCH_KEY)
    inherit_id = descriptor.get(INHERIT_KEY)
    explicit_kind = descriptor.get(KIND_KEY)
    weak_patch: Optional[Dict] = typed(raw_weak_patch, dict, {})
    strong_patch: Optional[Dict] = typed(raw_strong_patch, dict, {})
    host_class = cls

    if explicit_kind and not explicit_kind == host_class.__name__:
      host_class = cls.kind2cls(explicit_kind)
      if not host_class:
        err = f"no kind {explicit_kind} under {cls.__name__}"
        raise RuntimeError(f"[Model] FATAL {err}")

    if inherit_id:
      other: T = cls.inflate_with_str(inherit_id, **kwargs)
      host_class = other.__class__
      descriptor = utils.deep_merge(other.serialize(), descriptor)

    final_config = deepcopy(utils.deep_merge(
      weak_patch,
      descriptor,
      strong_patch
    ))
    model_instance = host_class(final_config)

    return model_instance

  @classmethod
  def global_provider_id(cls):
    raise NotImplemented

  @classmethod
  def from_provider(cls: Type[T], provider_kod: KoD = None) -> List[Model]:
    from kama_sdk.model.supplier.base.supplier import Supplier
    provider_kod = provider_kod or cls.global_provider_id()
    provider: Supplier = Supplier.inflate(provider_kod)
    return cls.inflate_many(provider.resolve())

  @classmethod
  def singleton_id(cls):
    raise NotImplemented

  @classmethod
  def inflate_singleton(cls: Type[T], **kwargs) -> T:
    return cls.inflate_with_str(cls.singleton_id(), **kwargs)

  @classmethod
  def lteq_classes(cls: Type[T]) -> List[Type[T]]:
    return models_manager.get_lteq_models(cls)

  @classmethod
  def kind2cls(cls: Type[T], kind: str) -> T:
    subclasses = cls.lteq_classes()
    matcher = lambda klass: klass.__name__ == kind
    return next(filter(matcher, subclasses), None)
