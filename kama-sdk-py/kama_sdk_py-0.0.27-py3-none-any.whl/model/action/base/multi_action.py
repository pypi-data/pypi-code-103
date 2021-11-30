from __future__ import annotations

from typing import List, Dict, Union, TypeVar

from kama_sdk.core.core import consts
from kama_sdk.core.core.types import ActionStatusDict, KoD, ErrorCapture
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.base.action_errors import ActionError
from kama_sdk.model.action.base.circuit_breaker import CircuitBreaker
from typing_extensions import TypedDict


class SubActionRule(TypedDict, total=False):
  action: KoD
  patch: Union[str, List[str]]
  _pass: str


T = TypeVar('T', bound='Action')


class MultiAction(Action):
  """
  Runs multiple sub_actions.
  """

  _final_sub_actions: List[T]
  _is_sub_actions_set: bool

  def __init__(self, config: Dict):
    super(MultiAction, self).__init__(config)
    self._final_sub_actions = []
    self._is_sub_actions_set = False

  def _load_sub_actions(self) -> List[T]:
    return self.inflate_children(Action, attr=SUB_ACTIONS_KEY)

  def are_sub_actions_ready(self) -> bool:
    return self.is_or_was_running()

  def get_circuit_breakers(self) -> List[CircuitBreaker]:
    return self.inflate_children(
      CircuitBreaker,
      attr=CIRCUIT_BREAKERS_KEY,
      safely=True
    )

  def get_final_sub_actions(self) -> List[T]:
    if not self._is_sub_actions_set:
      if self.are_sub_actions_ready():
        loaded_actions = self._load_sub_actions()
        self._final_sub_actions.extend(loaded_actions)
        self._is_sub_actions_set = True
    return self._final_sub_actions

  def perform(self):
    results = {}

    if self.handle_early_exit(-1):
      return results

    for index, action in enumerate(self.get_final_sub_actions()):
      ret = action.run()
      if issubclass(ret.__class__, Dict):
        results = {**results, **ret}
        self.patch(ret, invalidate=False)
      if self.handle_early_exit(index):
        return results
    return results

  def handle_early_exit(self, index: int) -> bool:
    """
    Returns true if positive early exit requested.
    :return:
    """
    if early_exit_status := self.on_sub_action_finished(index):
      if early_exit_status == consts.POS_STATUS:
        return True
      if early_exit_status in [consts.NEG_STATUS, consts.ERROR_STATUS]:
        raise ActionError(ErrorCapture(
          fatal=early_exit_status == consts.ERROR_STATUS,
          type='early_exit',
          reason='Early exit'
        ))

  def on_sub_action_finished(self, index: int):
    matcher = lambda cb: breaker_matches_action(cb, index)
    all_circuit_breakers = self.get_circuit_breakers()
    triggered_circuit_breakers = list(filter(matcher, all_circuit_breakers))
    for breaker in triggered_circuit_breakers:
      if breaker.is_triggered():
        return breaker.get_exit_status()
    return None

  def serialize_progress(self) -> ActionStatusDict:
    sub_actions = self.get_final_sub_actions()
    sub_progress = [a.serialize_progress() for a in sub_actions]
    own_progress = super(MultiAction, self).serialize_progress()
    return {**own_progress, **{'sub_items': sub_progress}}


def breaker_matches_action(breaker: CircuitBreaker, index: int) -> bool:
  return breaker.matches_action(index)


SUB_ACTIONS_KEY = 'sub_actions'
CIRCUIT_BREAKERS_KEY = 'circuit_breakers'
