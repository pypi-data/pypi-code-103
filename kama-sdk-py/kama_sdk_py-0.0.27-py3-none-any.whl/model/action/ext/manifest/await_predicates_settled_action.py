import time
from functools import lru_cache
from typing import List

from kama_sdk.core.core import consts
from kama_sdk.core.core.consts import RUNNING_STATUS, NEG_STATUS
from kama_sdk.core.core.types import ErrorCapture
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.base.action_errors import FatalActionError
from kama_sdk.model.action.base.multi_action import MultiAction
from kama_sdk.model.base import mc
from kama_sdk.model.base.common import PREDICATES_KEY
from kama_sdk.model.operation.predicate_statuses_computer import PredicateStatusesComputer
from kama_sdk.model.predicate.predicate import Predicate
from kama_sdk.utils.logging import lwar


class AwaitPredicatesSettledAction(MultiAction):
  """
  MultiAction that dynamically creates sub-actions from the predicates
  passed to it. Its execution is a busy loop that waits for either
  all optimist predicates to be `True`, or for one pessimist predicate
  to be `False`. It also terminates if the timeout `timeout_seconds: int`
  elapses.

  This list of predicates is special: it should contain
  optimist-pessimist siblings, where each optimist predicate has a
  pessimist twin. For the details of the demarcation of two
  siblings, see`twin_flip()`.
  """

  @lru_cache
  def get_predicates(self) -> List[Predicate]:
    return self.inflate_children(Predicate, attr=PREDICATES_KEY)

  def get_timeout_seconds(self) -> int:
    return self.get_attr(TIMEOUT_SECONDS_KEY, backup=180)

  def _load_sub_actions(self) -> List[Action]:
    predicates = self.get_predicates()
    optimists = [p for p in predicates if p.is_optimist()]
    return [self.pred2action(p) for p in optimists]

  def perform(self) -> None:
    predicates = self.get_predicates()
    computer = PredicateStatusesComputer(predicates)
    timeout_seconds = self.get_timeout_seconds()

    start_ts = time.time()
    did_time_out = True

    while time.time() - start_ts < timeout_seconds:
      [p.clear_cached_results() for p in predicates]
      computer.perform_iteration()
      self.update_action_statuses(computer)
      self.add_logs(computer.explanations)
      self.raise_for_negative_outcomes(computer)

      if computer.did_finish():
        did_time_out = False
        break
      else:
        time.sleep(2)

    raise_for_timeout(did_time_out)

  def find_action_by_pred(self, predicate_id: str) -> Action:
    def discriminator(action: Action) -> bool:
      action_predicate_id = action.get_config()[SYNTH_ACTION_PRED_ID_KEY]
      return action_predicate_id == predicate_id

    return next(filter(discriminator, self.get_final_sub_actions()))

  def update_action_statuses(self, computer: PredicateStatusesComputer):
    for predicate in computer.get_optimist_predicates():
      evaluation = computer.find_eval(predicate.get_id())
      if action := self.find_action_by_pred(predicate.get_id()):
        if evaluation.get('met'):
          action.set_status(consts.POS_STATUS)
        else:
          pessimistic_twin_eval_id = twin_flip(predicate.get_id())
          pessimistic_twin = computer.find_eval(pessimistic_twin_eval_id)
          if pessimistic_twin:
            if pessimistic_twin.get('met'):
              action.set_status(NEG_STATUS)
            else:
              action.set_status(RUNNING_STATUS)
          else:
            lwar(f"{predicate.get_id()} has no twin")
      else:
        lwar(f"{predicate.get_id()} has no twin")

    if computer.did_fail():
      for sub in self.get_final_sub_actions():
        if sub.is_running():
          sub.set_status(consts.IDLE_STATUS)

  def pred2action(self, predicate: Predicate) -> Action:
    return self.inflate_child(Action, kod={
      mc.ID_KEY: predicate.get_id(),
      mc.TITLE_KEY: predicate.get_title(),
      mc.INFO_KEY: predicate.get_info(),
      SYNTH_ACTION_PRED_ID_KEY: predicate.get_id()
    })

  @classmethod
  def raise_for_negative_outcomes(cls, computer: PredicateStatusesComputer):
    if computer.did_fail():
      predicate = computer.culprit_predicate()
      prefix = "raise_for_negative_outcomes predicate"
      lwar(f"{prefix}: {predicate.debug_bundle()}", sig=cls.__name__)

      raise FatalActionError(ErrorCapture(
        type='predicate_settle_negative',
        reason=f"\"{predicate.get_title()}\" failure status",
        extras=dict(
          predicate_id=predicate.get_id(),
          predicate_kind=predicate.get_kind(),
          **predicate.error_extras()
        )
      ))


def raise_for_timeout(timed_out: bool):
  if timed_out:
    raise FatalActionError(ErrorCapture(
      type="predicate_settle_timeout",
      reason="The predicates being evaluated did not "
             "reach a positive status in time."
    ))


def twin_flip(pred_id: str) -> str:
  if pred_id.endswith(f"-{consts.NEG_STATUS}"):
    return pred_id.replace(f"-{consts.NEG_STATUS}", f"-{consts.POS_STATUS}")
  else:
    return pred_id.replace(f"-{consts.POS_STATUS}", f"-{consts.NEG_STATUS}")


TIMEOUT_SECONDS_KEY = 'timeout_seconds'
SYNTH_ACTION_PRED_ID_KEY = 'predicate_id'
