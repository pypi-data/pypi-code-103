from datetime import datetime
from typing import Dict, Optional

from kama_sdk.core.core import consts
from kama_sdk.core.core.types import ExitStatuses, ActionOutcome

IDLE = 'idle'
RUNNING = 'running'
SETTLED_POS = 'positive'
SETTLED_NEG = 'negative'


class StepState:
  def __init__(self, step_sig: str, parent_op):
    self.step_sig: str = step_sig
    self.parent_op = parent_op
    self.started_at = datetime.now()
    self.chart_assigns: Dict = {}
    self.state_assigns: Dict = {}
    self.pref_assigns: Dict = {}
    self.action_outcome: Optional[ActionOutcome] = None
    self.action_telem = None
    self.exit_statuses: ExitStatuses = default_exit_statuses()
    self.committed_at = None
    self.terminated_at = None
    self.job_id = None

  def notify_vars_assigned(self, bundle: Dict):
    self.chart_assigns = bundle.get(consts.TARGET_STANDARD)
    self.state_assigns = bundle.get(consts.TARGET_STATE)
    self.pref_assigns = bundle.get(consts.TARGET_PREFS)

  def all_assigns(self):
    """
    Merges chart assigns and state assigns extracted from the commit outcome.
    :return:
    """
    return dict(
      **self.chart_assigns,
      **self.state_assigns,
      **self.pref_assigns
    )

  def persistable_assigns(self) -> Dict:
    return dict(
      **self.chart_assigns,
      **self.pref_assigns
    )

def default_exit_statuses() -> ExitStatuses:
  return ExitStatuses(positive=[], negative=[])
