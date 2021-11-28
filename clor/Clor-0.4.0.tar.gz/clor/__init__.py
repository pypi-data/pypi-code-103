import contextlib
import logging.config
from functools import reduce


__all__ = 'configure', 'resolve'


class Configurator(logging.config.BaseConfigurator):
  '''
  This class in combination with ``ConvertingDict`` overrides
  lazy conversion of ``logging.config`` to preemptive conversion
  to allow access patters beyond ``__getitem__`` and ``__pop__``.

  The preemptive conversion works recursively like:

    1. Each sub-dictionary is wrapped in ``ConvertingDict`` in
       ``Configurator.create_dict``,
    2. It calls ``ConvertingDict.convert_items`` that iterates on
       own key-value pairs and calls ``ConvertingMixin.convert_with_key``
       on each,
    3. ``ConvertingMixin.convert_with_key`` uses ``Configurator.convert``
       to convert the value,
    4. Repeat step 1 if the value is a dictionary.

  '''

  auto_factory = None
  '''Flag that controls auto-invocation of "()" factories'''

  config = None
  '''``ConvertingDict`` instance'''

  cfg_converter = None
  '''Name of cfg:// converter method'''

  def __init__(self, config, auto_factory = True):
    self.auto_factory = auto_factory

    # Defer conversion to allow self-referencing, i.e. cfg://
    self.config = self.create_dict(config, convert_items = False)
    self.cfg_converter = self.value_converters['cfg']

    # Result of 1-pass resolution of "()" and cfg:// depends on the
    # order of dictionary iteration. It may turn out that cfg://
    # resolved first and then the factory is called for all the
    # places. To make it deterministic on 1st we don't convert cfg://.
    # But for cfg:// entries alongside "()" resolution is done on the
    # first pass.
    with self.ensure_cfg(False):
      self.config.convert_items()
    self.config.convert_items()

  @contextlib.contextmanager
  def ensure_cfg(self, enabled):
    if enabled and 'cfg' not in self.value_converters:
      self.value_converters['cfg'] = self.cfg_converter
      yield
      self.value_converters.pop('cfg')
    elif not enabled and 'cfg' in self.value_converters:
      self.value_converters.pop('cfg')
      yield
      self.value_converters['cfg'] = self.cfg_converter
    else:
      yield

  def create_dict(self, config, convert_items = True):
    d = ConvertingDict(config)
    d.configurator = self
    if convert_items:
      d.convert_items()
    return d

  def convert(self, value):
    if isinstance(value, dict):
      if not isinstance(value, ConvertingDict):
        value = self.create_dict(value)
      else:
        # 2nd pass for deterministic cfg:// resolution
        value.convert_items()

      if self.auto_factory and '()' in value:
        with self.ensure_cfg(True):
          value.convert_items()
        value = self.configure_custom(value)

    return super().convert(value)


class ConvertingDict(logging.config.ConvertingDict):

  def convert_items(self):
    for k, v in self.items():
      self.convert_with_key(k, v)

  def __getitem__(self, key):
    return dict.__getitem__(self, key)

  def get(self, key, default = None):
    return dict.get(self, key, default)

  def pop(self, key, default = None):
    return dict.pop(self, key, default)


def merge(target, source):
  '''Deep ``dict`` merge'''

  result = target.copy()  # shallow copy
  stack = [(result, source)]
  while stack:
    currentTarget, currentSource = stack.pop()
    for key in currentSource:
      if key not in currentTarget:
        currentTarget[key] = currentSource[key]  # appending
      else:
        if isinstance(currentTarget[key], dict) and isinstance(currentSource[key], dict):
          currentTarget[key] = currentTarget[key].copy()  # nested dict copy
          stack.append((currentTarget[key], currentSource[key]))
        elif currentTarget[key] is not None and currentSource[key] is None:
          del currentTarget[key]  # remove key marked as None
        else:
          currentTarget[key] = currentSource[key]  # overriding

  return result


def configure(*args, **kwargs):
  '''Merged nested configuration dictionary is wrapped into a resolver'''

  merged = reduce(merge, args)
  return Configurator(merged, **kwargs).config


resolve = logging.config._resolve
