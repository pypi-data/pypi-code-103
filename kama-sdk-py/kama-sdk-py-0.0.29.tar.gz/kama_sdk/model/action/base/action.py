import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, TypeVar

from inflection import underscore
from rq import get_current_job
from rq.job import Job

from kama_sdk.core.core import job_client, status_manager
from kama_sdk.core.core.consts import RUNNING_STATUS, NEG_STATUS, POS_STATUS, IDLE_STATUS, ACTION_STATUSES
from kama_sdk.core.core.types import ActionStatusDict, ErrorCapture, EventCapture
from kama_sdk.core.telem.telem_manager import telem_manager
from kama_sdk.model.action.base.action_errors import ActionErrOrException, ActionError
from kama_sdk.model.base.model import Model
from kama_sdk.model.error.action_error_remediation_option import ActionErrorRemediationOption
from kama_sdk.utils import env_utils
from kama_sdk.utils.logging import exception2trace, lerr

T = TypeVar('T', bound='Action')

RemOption = ActionErrorRemediationOption

class Action(Model):
  """
  Wrapper around a publisher-defined action that handles
  meta-information around the actual action, such as status, errors,
  and telemetry.
  """
  _status: str
  _err_capture: Optional[ErrorCapture]
  telem_vid: str
  _logs: List[str]

  def __init__(self, config: Dict):
    super().__init__(config)
    self._status = IDLE_STATUS
    self._err_capture = None
    self._logs = []
    self.telem_vid = str(uuid.uuid4())

  def run(self) -> Any:
    outcome: Optional[Any]
    exception: Optional[Exception]
    err_capture: Optional[ErrorCapture] = None
    should_raise: bool = False

    try:
      self.set_running()
      outcome = self.perform()
      exception = None
    except Exception as _exception:
      outcome = None
      exception = _exception

    if exception:
      next_status = NEG_STATUS
      err_capture = exception2capture(self.telem_vid, exception)
      should_raise = err_capture['fatal']
      self.add_logs(err_capture.get('logs'))
    else:
      next_status = POS_STATUS

    self._err_capture = err_capture
    self.set_status(next_status)
    self.handle_telem()

    if should_raise:
      lerr("Action runtime exception", sig=self.sig())
      if err_capture['type'] == 'internal_error':
        lerr("", exc=exception)
      else:
        lerr(err_capture, sig=self.sig())
      raise ActionError(err_capture, is_original=False)

    return outcome

  def parent_telem_event_id(self):
    return self.get_attr(KEY_PARENT_EVENT_VID)

  def get_event_type(self):
    return self.get_attr(
      TELEM_EVENT_TYPE_KEY,
      lookback=False,
      backup=DEFAULT_EVENT_TYPE
    )

  def get_debug_attr_keys(self) -> List[str]:
    return self.get_local_attr(DEBUG_PROPS_KEY, backup=[])

  def gen_backup_event_name(self):
    return underscore(self.__class__.__name__)

  def handle_telem(self):
    telem_bundle = self.generate_telem_bundle()
    telem_manager.register_event(telem_bundle)

    if self._err_capture and self._err_capture['is_original']:
      telem_manager.register_error(self._err_capture)

    if self.am_root_action():
      if not env_utils.is_test():
        job_client.enqueue_telem_func(status_manager.full_sync)
        job_client.enqueue_telem_func(telem_manager.flush_flash)

  def generate_telem_bundle(self) -> EventCapture:
    parent_action = self.parent_action()
    parent_vid = parent_action.telem_vid if parent_action else None
    return EventCapture(
      vid=self.telem_vid,
      parent_vid=parent_vid,
      initiator_kind=None,
      initiator_id=None,
      connected_artifacts=[],
      type=self.get_event_type(),
      name=self.get_id() or self.gen_backup_event_name(),
      status=self.get_status(),
      logs=self._logs,
      occurred_at=str(datetime.now())
    )

  def get_error_capture(self) -> ErrorCapture:
    return self._err_capture

  def get_status(self) -> str:
    return self._status

  def is_running(self):
    return self.get_status() == RUNNING_STATUS

  def is_or_was_running(self):
    return self.get_status() in [RUNNING_STATUS, POS_STATUS, NEG_STATUS]

  def set_running(self):
    self.set_status(RUNNING_STATUS)

  def set_positive(self):
    self.set_status(POS_STATUS)

  def set_negative(self):
    self.set_status(NEG_STATUS)

  def set_status(self, status):
    assert status in ACTION_STATUSES
    self._status = status
    self.notify_job()

  def perform(self) -> Optional[Dict]:
    raise NotImplementedError

  def add_logs(self, new_logs: Optional[List[str]]) -> None:
    new_logs = new_logs or []
    self._logs = [*self._logs, *new_logs]

  def get_logs(self) -> List[str]:
    return self._logs

  def parent_action(self) -> Optional[T]:
    if parent := self.get_parent():
      if issubclass(parent.__class__, Action):
        return parent
    return None

  def am_sub_action(self) -> bool:
    return issubclass(self._parent.__class__, Action)

  def am_root_action(self):
    return not self.am_sub_action()

  def find_root_action(self) -> Optional:
    if self.am_root_action():
      return self
    elif parent_action := self.parent_action():
      return parent_action.find_root_action()
    else:
      return None

  def notify_job(self):
    job: Job = get_current_job()
    if job:
      action_root = self.find_root_action()
      if action_root:
        progress_bundle = action_root.serialize_progress()
        job.meta['progress'] = json.dumps(progress_bundle)
        job.save_meta()
      else:
        print(f"[action:{self.get_id}] danger root not found")

  def gen_debug_dump(self) -> Dict:
    bundle = {}
    for attr_name in self.get_debug_attr_keys():
      try:
        bundle[attr_name] = self.get_attr(attr_name)
      except RuntimeError as e:
        bundle[attr_name] = f"[error] {str(e)}"
    return bundle

  def serialize_progress(self) -> ActionStatusDict:
    return dict(
      id=self.get_id(),
      title=self.get_title(),
      info=self.get_info(),
      status=self.get_status(),
      sub_items=[],
      logs=self._logs,
      debug=self.gen_debug_dump(),
      error=err2client_facing(self._err_capture)
    )


def err2client_facing(err_capt: ErrorCapture) -> Optional[Dict]:
  if err_capt:
    return dict(
      fatal=err_capt.get('fatal', True),
      type=err_capt.get('type'),
      reason=err_capt.get('reason'),
      logs=err_capt.get('logs', []),
      remediation_options=serialize_remediation_options(err_capt)
    )
  else:
    return None


def serialize_remediation_options(err_capture: ErrorCapture) -> List[Dict]:
  rems: List[RemOption] = RemOption.matching_error_capture(err_capture)
  return [rem.serialize_for_client() for rem in rems]


def exception2capture(vid: str, exception: ActionErrOrException) -> ErrorCapture:
  err_capture: Optional[ErrorCapture] = None

  if issubclass(exception.__class__, ActionError):
    err_capture = exception.err_capture

  if not err_capture:
    err_capture = ErrorCapture(
      fatal=True,
      type="internal_error",
      reason=f"{exception.__class__.__name__}: {str(exception)}",
      logs=exception2trace(exception)
    )

  if not err_capture.get('type'):
    err_capture['type'] = 'unknown_error_type'

  if not err_capture.get('reason'):
    err_capture['reason'] = exception.__class__.__name__

  if 'is_original' not in err_capture.keys():
    err_capture['is_original'] = True

  err_capture['occurred_at'] = str(datetime.now())

  err_capture['event_vid'] = vid
  return err_capture


DEBUG_PROPS_KEY = 'debug_props'
TELEM_ENABLED_KEY = 'telem'
TELEM_PROPS_KEY = 'telem_props'
ERROR_TELEM_PROPS_KEY = 'error_telem_props'
ERROR_TELEM_KEY = 'error_telem'
TELEM_EVENT_TYPE_KEY = 'telem_type'

KEY_PARENT_EVENT_VID = 'parent_event_virtual_id'
KEY_PARENT_EVENT_ID = 'parent_event_id'

DEFAULT_EVENT_TYPE = 'action'
OP_STEP_EVENT_TYPE = 'operation_step'
PREFLIGHT_EVENT_TYPE = 'preflight_check'
SYS_CHECK_EVENT_TYPE = 'system_check'
SET_VAR_EVENT_TYPE = 'set_var'
UNSET_VAR_EVENT_TYPE = 'unset_var'
