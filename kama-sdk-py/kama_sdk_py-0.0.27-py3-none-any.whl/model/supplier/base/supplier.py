from typing import Any, Dict, Union, Optional, List

import jq

from kama_sdk.model.base import mc
from kama_sdk.model.base.model import Model
from kama_sdk.utils import utils
from kama_sdk.utils.logging import lwar, lerr


lookback = mc.PARENT_LOOKBACK_ENABLED_FLAG
backup = mc.BACKUP_KW

class Supplier(Model):

  def get_output_spec(self) -> Union[str, Dict]:
    """
    Returns the 'output' attribute value, which is the
    serializer-specific instruction for how the serialization happens
    :return:
    """
    return self.get_local_attr(OUTPUT_FMT_KEY)

  def write_source_data(self, new_value: Any):
    self.patch({SRC_DATA_KEY: new_value})

  def get_resolve_depth(self) -> Optional[int]:
    return self.get_local_attr(RESOLVE_DEPTH_KEY)

  def get_source_data(self) -> Optional[any]:
    """
    Returns "source" from the descriptor, which is treated as the
    "main input" by most supplier subclasses.
    :return:
    """
    return self.get_local_attr(SRC_DATA_KEY)

  def get_serializer_type(self) -> str:
    """
    Returns the 'serializer' in the descriptor, used as an enum to
    select the serialization logic (if any) that gets applied to the
    computed result.
    :return:
    """
    value = self.get_local_attr(SERIALIZER_KEY, **{backup: SER_JQ})
    return self.type_check(SERIALIZER_KEY, value, str)

  def get_many_directive(self) -> Optional[bool]:
    """
    Returns the value for 'many' in the descriptor, used by some
    serializers to handle lists.
    :return:
    """
    return self.get_local_attr(IS_MANY_KEY)

  def get_attrs_to_print(self) -> List[str]:
    return self.get_config().get(PRINT_DEBUG_KEY, [])

  def print_debug(self):
    attr_keys = self.get_attrs_to_print()
    for attr_key in attr_keys:
      value = self.get_attr(attr_key)
      lwar(f"[{self.get_id()}] {attr_key} = {value}")

  def resolve(self) -> Any:
    """
    Central function for the Supplier base class. Invokes the
    'actual worker'
    :return:
    """
    self.print_debug()
    computed_value = self._compute()
    serializer_type = self.get_serializer_type()

    if isinstance(computed_value, dict):
      if depth := self.get_resolve_depth():
        computed_value = self.resolve_attr_value(computed_value, depth=depth)

    if serializer_type:
      if serializer_type == SER_NATIVE:
        serialized_value = self.do_native_serialize(computed_value)
      elif serializer_type == SER_JQ:
        serialized_value = self.do_jq_serialize(computed_value)
      elif serializer_type == SER_MODEL_ATTR:
        serialized_value = self.do_model_attr_serialize(computed_value)
      elif serializer_type == SER_MODEL_STR:
        serialized_value = self.do_str_serialize(computed_value)
      else:
        lwar(f"illegal serialize type {serializer_type}")
        serialized_value = computed_value
    else:
      serialized_value = computed_value

    return serialized_value

  def get_lookup_options(self):
    value = self.get_config().get(LOOKUP_OPTIONS_KEY) or {}
    return self.type_check(LOOKUP_OPTIONS_KEY, value, Dict, alt={})

  @staticmethod
  def do_str_serialize(computed_value) -> str:
    if computed_value:
      return str(computed_value)
    else:
      return ""

  def do_model_attr_serialize(self, computed_value) -> Any:
    if isinstance(computed_value, Model):
      key = self.get_output_spec()
      lookup_opts = self.get_lookup_options()
      return computed_value.get_attr(key, lookup_opts=lookup_opts)
    else:
      exp = f"{computed_value} as a model; its is a {type(computed_value)}"
      lerr(f"Cannot access {exp}. returning None", sig=self.sig())
      return None

  def do_jq_serialize(self, value: Any) -> Any:
    spec = self.get_output_spec()
    if spec and value is not None:
      try:
        expression = jq.compile(spec)
        if self.get_many_directive():
          return expression.input(value).all()
        else:
          return expression.input(value).first()
      except Exception as e:
        detail = f"expr({spec}) for {type(value)} {value}"
        lerr(f"jq compile failed: {str(e)} on {detail}", sig=self.sig())
        return None
    else:
      return value

  def do_native_serialize(self, computed_value) -> Any:
    treat_as_list = self.get_many_directive()
    is_listy_result = utils.is_listy(computed_value)
    output_fmt = self.get_output_spec()

    # TODO once all green remove 'auto'
    if treat_as_list in [None, 'auto', '']:
      treat_as_list = is_listy_result

    treat_as_count = output_fmt == NATIVE_COUNT_TOK

    if treat_as_list and not treat_as_count:
      if is_listy_result:
        return [self.serialize_item(item) for item in computed_value]
      else:
        return [self.serialize_item(computed_value)]
    else:
      if not is_listy_result or treat_as_count:
        return self.serialize_item(computed_value)
      else:
        item = computed_value[0] if len(computed_value) > 0 else None
        return self.serialize_item(item) if item else None

  def _compute(self) -> Any:
    return self.get_source_data()

  def serialize_item(self, item: Any) -> Union[Dict, str]:
    fmt = self.get_output_spec()
    if not fmt or type(fmt) == str:
      return self.serialize_item_prop(item, fmt)
    elif type(fmt) == dict:
      return self.serialize_dict_item(item)
    else:
      return ''

  def serialize_dict_item(self, item):
    fmt: Dict = self.get_output_spec()
    serialized = {}
    for key, value in list(fmt.items()):
      serialized[key] = self.serialize_item_prop(item, value)
    return serialized

  # noinspection PyBroadException
  @staticmethod
  def serialize_item_prop(item: Any, prop_name: Optional[str]) -> Optional[Any]:
    if prop_name:
      if prop_name == NATIVE_IDENTITY_TOK:
        return item
      elif prop_name == NATIVE_COUNT_TOK:
        try:
          return len(item)
        except:
          return 0
      else:
        try:
          return utils.pluck_or_getattr_deep(item, prop_name)
        except:
          return None
    else:
      return item


SER_JQ = 'jq'
SER_NATIVE = 'native'
SER_MODEL_ATTR = 'attr'
SER_MODEL_STR = 'str'

RESOLVE_DEPTH_KEY = 'depth'
IS_MANY_KEY = 'many'
OUTPUT_FMT_KEY = 'output'
ON_RAISE_KEY = 'on_error'
SRC_DATA_KEY = 'source'
SERIALIZER_KEY = 'serializer'
PRINT_DEBUG_KEY = 'print_debug'
LOOKUP_OPTIONS_KEY = "lookup_options"

NATIVE_IDENTITY_TOK = "__identity__"
NATIVE_COUNT_TOK = '__count__'
