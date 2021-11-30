from typing import Dict

from kama_sdk.core.core.types import ErrorCapture, EventCapture
from kama_sdk.model.action.base.action import Action, ActionError, SYS_CHECK_EVENT_TYPE, TELEM_EVENT_TYPE_KEY
from kama_sdk.model.base.common import PREDICATE_KEY
from kama_sdk.model.predicate.predicate import Predicate
from kama_sdk.utils.utils import any2bool


class RunPredicateAction(Action):
  """
  Action that evaluates a single predicate. If the predicate resolves
  to True, the action status will be positive. If the predicate resolves
  to False, the action will raise an ActionError where `fatal` is
  set to the value of `false_is_fatal` (False by default).

  The underlying predicate's `id`, `title`, `info`,
  are used as the action's own unless the action supplies explicit ones.
  The predicate's `reason` is given used as the ErrorCapture's `reason`.
  """

  def __init__(self, config: Dict):
    super().__init__(config)
    self._id_hack = None

  def get_id(self) -> str:
    from_super = super().get_id()
    return from_super or self.get_predicate().get_id()

  def get_title(self):
    return super().get_title() or self.get_predicate().get_title()

  def get_info(self):
    return super().get_info() or self.get_predicate().get_info()

  def should_abort_on_false(self) -> bool:
    raw_value = self.get_attr(ABORT_ON_FAIL_KEY, backup=False)
    return any2bool(raw_value)

  def get_predicate(self) -> Predicate:
    return self.inflate_child(Predicate, attr=PREDICATE_KEY)

  def perform(self) -> None:
    predicate = self.get_predicate()
    if not predicate.resolve():
      raise ActionError(ErrorCapture(
        fatal=self.should_abort_on_false(),
        type='negative_predicate',
        reason=predicate.get_reason(),
        extras=dict(
          predicate_id=predicate.get_id(),
          predicate_kind=predicate.kind(),
          predicate_challlenge=predicate.get_challenge(),
          predicate_check_against=predicate.get_check_against(),
          **predicate.error_extras()
        )
      ))

  def generate_telem_bundle(self) -> EventCapture:
    default = super(RunPredicateAction, self).generate_telem_bundle()
    predicate = self.get_predicate()
    return EventCapture(
      **default,
      initiator_kind=predicate.get_kind(),
      initiator_id=predicate.get_id()
    )

  def get_event_type(self):
    if explicit := self.get_local_attr(TELEM_EVENT_TYPE_KEY):
      return explicit
    else:
      return SYS_CHECK_EVENT_TYPE


ABORT_ON_FAIL_KEY = 'false_is_fatal'
