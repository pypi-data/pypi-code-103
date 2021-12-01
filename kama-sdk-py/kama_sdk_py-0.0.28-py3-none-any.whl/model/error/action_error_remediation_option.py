from functools import lru_cache
from typing import Optional, Dict, List

from kama_sdk.core.core.structured_search import is_query_match
from kama_sdk.core.core.types import ErrorCapture
from kama_sdk.model.base.model import Model


class ActionErrorRemediationOption(Model):

  def get_matcher(self) -> Dict:
    return self.get_attr(PRED_MATCHER_KEY, depth=0)

  def matches_error_capture(self, error_capture: ErrorCapture) -> bool:
    if matcher := self.get_matcher():
      return is_query_match(matcher, error_capture)
    else:
      return False

  @lru_cache
  def button_action_desc(self) -> Optional[Dict]:
    return self.get_attr(BUTTON_KEY, lookback=False, depth=100)

  @classmethod
  def matching_error_capture(cls, err_capture: ErrorCapture):
    self_instances = cls.inflate_all()
    decider = lambda inst: inst.matches_error_capture(err_capture)
    return list(filter(decider, self_instances))

  def serialize_for_client(self) -> Dict:
    return {
      'title': self.get_title(),
      'info': self.get_info(),
      'button_action': self.button_action_desc()
    }


BUTTON_KEY = 'button_action'
PRED_MATCHER_KEY = 'match'
