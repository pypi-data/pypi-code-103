from typing import List

from kama_sdk.core.core import config_man as cm
from kama_sdk.core.core import config_man as cman_module
from kama_sdk.core.core.config_man import config_man
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.base.common import VARS_LEVEL_KEY
from kama_sdk.model.base.model_decorators import model_attr


class UnsetManifestVarsAction(Action):

  def get_id(self) -> str:
    return super().get_id() or DEFAULT_ID

  def get_title(self) -> str:
    return super().get_title() or default_title(self.get_vars_level())

  def get_info(self) -> str:
    return super().get_info() or default_info(self.get_vars_level())

  @model_attr()
  def get_vars_level(self) -> str:
    return self.get_attr(VARS_LEVEL_KEY, backup=cm.USER_VARS_LVL)

  @model_attr()
  def victim_keys(self) -> List[str]:
    return self.get_attr(VICTIM_KEYS_KEY, backup=[])

  def perform(self) -> None:
    self.victim_keys()
    source_key = self.get_vars_level()
    victim_keys = self.victim_keys()
    self.add_logs([f"unset {source_key}from  {victim_keys}"])
    config_man.unset_deep_vars(
      source_key,
      victim_keys,
      **{cman_module.SPACE_KW: self.get_config_space()}
    )


def default_title(entry_key: str) -> str:
  return f"Unset entries in {entry_key}"


def default_info(entry_key: str) -> str:
  return f"Delete entries from {entry_key} " \
         f"allowing them to be overtaken"


DEFAULT_ID = "sdk.action.unset_vars"
VICTIM_KEYS_KEY = 'victim_keys'
