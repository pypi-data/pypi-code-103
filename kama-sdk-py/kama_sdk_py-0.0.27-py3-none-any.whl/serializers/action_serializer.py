from typing import Dict

from kama_sdk.model.action.base.action import Action


def serialize_std(action: Action) -> Dict:
  return dict(
    id=action.get_id(),
    title=action.get_title(),
    info=action.get_info(),
    tags=action.get_tags(),
    space=action.get_space_id()
  )
