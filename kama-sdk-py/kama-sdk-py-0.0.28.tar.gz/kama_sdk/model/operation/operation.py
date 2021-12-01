from typing import List, Optional

from kama_sdk.model.action.base.action import PREFLIGHT_EVENT_TYPE, TELEM_EVENT_TYPE_KEY
from kama_sdk.model.base.common import PREDICATES_KEY
from kama_sdk.model.base.mc import ATTR_KW, ID_KEY, TITLE_KEY, INFO_KEY
from kama_sdk.model.base.model import Model
from kama_sdk.model.operation.operation_state import OperationState
from kama_sdk.model.operation.step import Step
from kama_sdk.model.predicate.multi_predicate import MultiPredicate
from kama_sdk.model.predicate.predicate import Predicate


class Operation(Model):

  def get_steps(self) -> List[Step]:
    """
    Loads the Steps associated with the Stage.
    :return: List of Step instances.
    """
    return self.inflate_children(Step, **{ATTR_KW: STEPS_KEY})

  def find_step_by_id(self, step_id: str) -> Step:
    """
    Finds the Step by key and inflates (instantiates) into a Step instance.
    :param step_id: identifier for desired Step.
    :return: Step instance.
    """
    matcher = lambda step: step.get_id() == step_id
    return next(filter(matcher, self.get_steps()), None)

  def get_first_step_id(self) -> Optional[str]:
    """
    Returns the key of the first associated Step, if present.
    :return: Step key or None.
    """
    if len(steps := self.get_steps()) > 0:
      return steps[0].get_id()
    return None

  def compute_next_step_id(self, crt_step: Step, op_state: OperationState) -> str:
    """
    Returns the id of the next step, or "done" if no next step exists.
    :param crt_step:
    :param op_state: if-then-else values, if necessary.
    :return: id of next step or "done".
    """
    if override_value := crt_step.compute_next_step_id(op_state):
      return override_value
    else:
      steps = self.get_steps()
      index = get_step_index(steps, crt_step.get_id())
      is_not_last = index < len(steps) - 1
      return steps[index + 1].get_id() if is_not_last else 'done'

  def get_preflight_predicates(self) -> List[Predicate]:
    return self.inflate_children(
      Predicate,
      attr=PREFLIGHT_PREDICATES_KEY
    )

  def generate_preflight_multi_predicate(self) -> Optional[MultiPredicate]:
    predicates = self.get_preflight_predicates()
    if predicates and len(predicates) > 0:
      return MultiPredicate.inflate({
        ID_KEY: f"{self.get_id()}.preflight-predicate",
        TITLE_KEY: "Operation Preflight Checks",
        INFO_KEY: "Test battery to preempt issues",
        PREDICATES_KEY: [p.get_config() for p in predicates]
      })
    else:
      return None


def get_step_index(steps: List[Step], step_id: str) -> int:
  """
  Returns the index of the desired Step.
  :param steps: list of Steps to search from.
  :param step_id: id to identify the desired Step.
  :return: index of the desired Step.
  """
  finder = (i for i, step in enumerate(steps) if step.get_id() == step_id)
  return next(finder, None)


telem_patch = {TELEM_EVENT_TYPE_KEY: PREFLIGHT_EVENT_TYPE}
STEPS_KEY = 'steps'
PREFLIGHT_PREDICATES_KEY = 'preflight_predicates'
