from typing import Any, Optional

from kama_sdk.core.core import config_man as cman_module
from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.core.types import KteaDict
from kama_sdk.core.ktea.ktea_provider import ktea_client
from kama_sdk.model.supplier.base.supplier import Supplier


reload_kw = cman_module.RELOAD_KWARG
space_kw = cman_module.SPACE_KW


class ConfigSupplier(Supplier):
  """
  Given a target field and space, supplies the value of that field for
  that space in the kamafile. Reload options can also be customized.
  """
  def get_field_key(self) -> str:
    return self.get_attr(FIELD_KEY) or cman_module.USER_VARS_LVL

  def get_should_reload_cmap_directive(self) -> Optional[bool]:
    return self.get_attr(RELOAD_CMAP_KEY, backup=None)

  def _compute(self) -> Any:
    """
    Performs operation described in the class-level documentation.
    :return:
    """
    field_name = self.get_field_key()
    should_reload = self.get_should_reload_cmap_directive()
    space = self.get_config_space()
    down_kwargs = {reload_kw: should_reload, space_kw: space}
    return config_man.read_typed_entry(field_name, **down_kwargs)


class NamespaceSupplier(Supplier):
  """
  Supplies the installation/NMachine's namespace.
  """
  def _compute(self) -> Any:
    return config_man.get_ns()


class MergedVarsSupplier(Supplier):
  """
  For a given space, supplies the merged Dict of manifest
  variables.

  """
  def _compute(self) -> Any:
    down_kwargs = {space_kw: self.get_config_space()}
    return config_man.get_merged_vars(**down_kwargs)


class DefaultVariablesSupplier(Supplier):
  def _compute(self) -> Any:
    kwargs = {space_kw: self.get_config_space()}
    return config_man.get_default_vars(**kwargs)


class PresetAssignmentsSupplier(Supplier):

  def optional_ktea_desc(self) -> KteaDict:
    return self.get_attr(KTEA_KEY, depth=100, lookback=False)

  def _compute(self) -> Any:
    client_inst = ktea_client(
      space=self.get_config_space(),
      ktea=self.optional_ktea_desc()
    )
    return client_inst.load_preset(self.get_source_data())


SPECIAL_NS_KEY = "ns"
KTEA_KEY = 'ktea'
FIELD_KEY = 'field_key'
RELOAD_CMAP_KEY = 'reload'
