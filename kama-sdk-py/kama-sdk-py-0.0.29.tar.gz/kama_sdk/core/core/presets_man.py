from typing import List, Optional, Dict

from kama_sdk.core.core import job_client
from kama_sdk.model.action.base.action import TELEM_EVENT_TYPE_KEY
from kama_sdk.model.base.common import VALUES_KEY
from kama_sdk.utils import utils
from kama_sdk.core.core.config_man import config_man
from kama_sdk.model.action.base import action
from kama_sdk.model.base import mc
from kama_sdk.model.variable.preset import Preset
from kama_sdk.model.variable.manifest_variable import ManifestVariable


def ser_preset(preset: Preset, var_models: List[ManifestVariable]):
  assignments = preset.get_variable_assignments()
  flat_assigns = utils.deep2flat(assignments)

  def find_var(key: str) -> Optional[ManifestVariable]:
    disc = lambda _model: _model.get_id() == key
    return next(filter(disc, var_models), None)

  var_bundles = []
  for k, v in flat_assigns.items():
    var_model = find_var(k)
    var_bundles.append(dict(
      id=k,
      info=var_model.get_info() if var_model else None,
      new_value=v,
      old_value=var_model.get_current_value(reload=False) if var_model else None
    ))

  return dict(
    id=preset.get_id(),
    title=preset.get_title(),
    info=preset.get_info(),
    variables=var_bundles
  )


def load_all(space: str):
  config_man.invalidate_cmap()
  presets = Preset.inflate_all(q=space_q(space))
  var_models = ManifestVariable.inflate_all(q=space_q(space))
  return [ser_preset(p, var_models) for p in presets]


def load_and_start_apply_job(preset_id: str, space: str, whitelist: List[str]):
  config_man.invalidate_cmap()
  preset = Preset.inflate(preset_id, q=space_q(space))

  if preset.is_default():
    assignments = {}
  else:
    flat_assigns: Dict = utils.deep2flat(preset.get_variable_assignments())
    if whitelist:
      flat_assigns = {k: v for k, v in flat_assigns.items() if k in whitelist}
    assignments = utils.flat2deep(flat_assigns)

  return job_client.enqueue_action(
    'sdk.action.commit_template_apply_safely',
    patch={
      VALUES_KEY: assignments,
      TELEM_EVENT_TYPE_KEY: action.SET_VAR_EVENT_TYPE
    }
  )


def space_q(space: str) -> Dict:
  return {mc.SPACE_KEY: space}
