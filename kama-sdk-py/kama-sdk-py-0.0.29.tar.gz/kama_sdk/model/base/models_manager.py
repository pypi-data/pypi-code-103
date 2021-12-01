from __future__ import annotations

from copy import deepcopy
from typing import List, Dict, Optional, Type, TypeVar

from kama_sdk.core.core import structured_search
from kama_sdk.core.core.consts import APP_SPACE_ID
from kama_sdk.model.base.default_models import default_model_classes
from kama_sdk.model.base.mc import SPACE_KEY, CONFIG_SPACE_KEY, LABELS_KEY

from kama_sdk.model.base.mc import ID_KEY, KIND_KEY
from kama_sdk.utils import utils, descriptor_utils, asset_utils
from kama_sdk.utils.descriptor_utils import debug_sig
from kama_sdk.utils.logging import lwar

T = TypeVar('T', bound='Model')

class ModelsManager:
  _descriptors: List[Dict]
  _classes: List[Type[T]]
  _asset_paths: List[str]

  def __init__(self):
    self._descriptors = []
    self._classes = []
    self._asset_paths = []

  def add_descriptors(self, descriptors: List[Dict]):
    """
    Calls add_any_descriptors with space=app
    :param descriptors:
    :return:
    """
    self.add_any_descriptors(descriptors, APP_SPACE_ID)

  def add_any_descriptors(self, descriptors: List[Dict], space=None):
    """
    Register model descriptors `descriptors`. If a `space` is given,
    all top-level descriptors get patched with `space: <space>`; if one
    has a non-nil `space` not equal to the supplied `space`, the explicit
    space is NOT overwritten, a warning is shown instead.
    :param descriptors:
    :param space:
    :return:
    """

    if not isinstance(descriptors, list):
      lwar(f"add_descriptors given non-list {descriptors}", sig=self.sig())
      return

    for _desc in descriptors:
      if isinstance(_desc, dict):
        descriptor = deepcopy(_desc)

        if descriptor.get(LABELS_KEY) is None:
          descriptor[LABELS_KEY] = {}

        if space:
          if declared_space := descriptor.get(SPACE_KEY):
            if declared_space != space:
              msg = f"explicit space {declared_space} != {space} " \
                    f"for descriptor {debug_sig(descriptor)}"
              lwar(msg, sig=self.sig())
          else:
            descriptor[SPACE_KEY] = space

          if not descriptor.get(CONFIG_SPACE_KEY):
            descriptor[CONFIG_SPACE_KEY] = space

        self._descriptors.append(descriptor)
      else:
        m = f"{type(_desc)}: {_desc}"
        lwar(f"ignoring non-dict descriptor {m}", sig=self.sig())

  def add_models(self, model_classes: List[Type[T]]):
    """
    Register `Model` subclasses.
    :param model_classes:
    :return:
    """
    if isinstance(model_classes, list):
      from kama_sdk.model.base.model import Model
      for model_class in model_classes:
        is_type_good = False
        if isinstance(model_class, type):
          if issubclass(model_class, Model):
            is_type_good = True
        if is_type_good:
          self._classes.append(model_class)
        else:
          lwar(f"not adding non-model class {model_class}", sig=self.sig())
    else:
      lwar(f"add_models given non-list {model_classes}", sig=self.sig())

  def add_asset_dir_paths(self, paths: List[str]):
    self._asset_paths.extend(paths)

  def add_defaults(self):
    self.add_any_descriptors(descriptor_utils.load_sdk_defaults())
    self.add_models(default_model_classes())
    self.add_asset_dir_paths(asset_utils.load_sdk_defaults())

  def clear(self, restore_defaults=True):
    """
    Unregister all models and descriptors, including from SDK. If
    `restore_defaults` is true, adds back all SDK models/descriptors
    after unregister.
    :param restore_defaults:
    :return:
    """
    self._descriptors = []
    self._classes = []
    if restore_defaults:
      self.add_defaults()

  def query_descriptors(self, query_expr=None) -> List[Dict]:
    return structured_search.query(query_expr, self._descriptors)

  def get_descriptors(self, selector=None) -> List[Dict]:
    if selector:
      def discriminator(descriptor: Dict) -> bool:
        labels = descriptor.get(LABELS_KEY) or {}
        return utils.selects_labels(selector, labels)
      return list(filter(discriminator, self._descriptors))
    else:
      return self._descriptors

  def get_model_classes(self) -> List[Type[T]]:
    return self._classes

  def asset_dir_paths(self) -> List[str]:
    return self._asset_paths

  def find_any_class_by_name(self, name: str) -> Type[T]:
    matcher = lambda klass: klass.__name__ == name
    return next(filter(matcher, self.get_model_classes()), None)

  def find_any_config_by_id(self, _id: str) -> Dict:
    matcher = lambda c: c.get(ID_KEY) == _id
    return next(filter(matcher, self.get_descriptors()), None)

  def get_lteq_models(self, base_class: Type[T]) -> List[Type[T]]:
    pool = [*self.get_model_classes(), base_class]
    return [klass for klass in pool if issubclass(klass, base_class)]

  def find_desc_in_subtree(self, _id: str, base_cls: Type[T], query: Optional[str]):
    candidate_subclasses = self.get_lteq_models(base_cls)
    candidate_kinds = [klass.__name__ for klass in candidate_subclasses]
    candidate_configs = models_manager.query_descriptors(query)
    return self.find_config_by_id(_id, candidate_configs, candidate_kinds)

  def find_model_class(self, name: str, base_cls: Type[T]) -> Type[T]:
    classes = self.get_lteq_models(base_cls)
    matcher = lambda klass: klass.__name__ == name
    return next(filter(matcher, classes), None)

  @staticmethod
  def find_config_by_id(_id: str, configs: List[Dict], kinds: List[str]) -> Dict:
    def matcher(descriptor: Dict) -> bool:
      return descriptor.get(ID_KEY) == _id and \
             descriptor.get(KIND_KEY) in kinds
    return next(filter(matcher, configs), None)

  @staticmethod
  def configs_for_classes(configs: List[Dict], cls_pool: List[T]) -> List[Dict]:
    kinds_pool = [cls.__name__ for cls in cls_pool]
    return [c for c in configs if c.get(KIND_KEY) in kinds_pool]

  @staticmethod
  def sig():
    return "models_manager"


models_manager = ModelsManager()
