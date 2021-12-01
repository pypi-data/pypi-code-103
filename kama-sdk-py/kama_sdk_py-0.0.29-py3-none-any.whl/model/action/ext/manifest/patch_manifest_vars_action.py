from typing import Dict

import yaml

from kama_sdk.core.core import config_man as cman_module
from kama_sdk.core.core.config_man import config_man, USER_VARS_LVL
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.base.common import VALUES_KEY, VARS_LEVEL_KEY
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.utils import utils


class PatchManifestVarsAction(Action):

  @model_attr()
  def get_title(self) -> str:
    return super().get_title() or \
           f"Patch {self.get_target_key()} values"

  @model_attr()
  def get_info(self) -> str:
    return super().get_info() or \
           f"Merge new value into existing {self.get_target_key()}"

  def get_values(self) -> Dict:
    raw = self.get_attr(VALUES_KEY) or {}
    return utils.flat2deep(raw)

  @model_attr()
  def get_target_key(self) -> str:
    return self.get_attr(VARS_LEVEL_KEY, backup=USER_VARS_LVL)

  def perform(self) -> None:
    source_key = self.get_target_key()
    values = self.get_values()

    log = f"patching {self.get_config_space()}/{source_key} with"
    self.add_logs([f"{log}", yaml.dump(values)])

    config_man.patch_into_deep_dict(
      source_key,
      values,
      **{cman_module.SPACE_KW: self.get_config_space()}
    )
