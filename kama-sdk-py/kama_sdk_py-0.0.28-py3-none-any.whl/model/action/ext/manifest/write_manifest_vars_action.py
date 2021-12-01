from typing import Dict, Optional

from kama_sdk.core.core import config_man as cman_module
from kama_sdk.core.core.config_man import config_man, MANIFEST_VAR_LEVEL_KEYS
from kama_sdk.core.core.types import ErrorCapture
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.base.action_errors import FatalActionError
from kama_sdk.model.base.common import VALUES_KEY, VARS_LEVEL_KEY
from kama_sdk.model.base.mc import TITLE_KEY
from kama_sdk.model.base.model_decorators import model_attr


class WriteManifestVarsAction(Action):
  """
  Completely overwrites a variables bundle in the Kamafile.
  Which bundle is determined by the `target_key`, which must be one of
  `"default_vars"`, `"vendor_injection_vars"` ,`"user_vars"`.

  Because this is a potentially destructive action, the `target_key`
  must be made explicit. If it is missing or not in the list above,
  a `FatalActionError` is raised.
  """
  def get_id(self) -> str:
    return super().get_id() or DEFAULT_ID

  def get_title(self) -> Optional[str]:
    return self.get_local_attr(TITLE_KEY) or \
           f"Overwrite {self.get_vars_level_id()} variables"

  def get_info(self) -> Optional[str]:
    return super().get_info() or self.get_title()

  def values(self) -> Dict:
    return self.get_attr(VALUES_KEY) or {}

  @model_attr()
  def get_vars_level_id(self) -> str:
    return self.get_attr(VARS_LEVEL_KEY)

  def perform(self) -> None:
    self.raise_if_illegal_source_key()
    config_man.write_typed_entry(
      self.get_vars_level_id(),
      self.values(),
      **{cman_module.SPACE_KW: self.get_config_space()}
    )

  def raise_if_illegal_source_key(self):
    reason = None
    source_key = self.get_vars_level_id()
    if not source_key:
      reason = "source key must be explicit for dangerous action"
    elif source_key not in MANIFEST_VAR_LEVEL_KEYS:
      reason = f"source key {source_key} not in {MANIFEST_VAR_LEVEL_KEYS}"

    if reason:
      raise FatalActionError(ErrorCapture(
        type='write_manifest_action_illegal_key',
        reason=reason
      ))


DEFAULT_ID = "sdk.action.write_manifest_variables"
