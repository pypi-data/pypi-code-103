import json
from functools import lru_cache
from typing import Optional, Dict, Callable

from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from kama_sdk.cli.worker_cli_entrypoint import conn
from kama_sdk.core.core import consts
from kama_sdk.core.core.consts import POS_STATUS, NEG_STATUS, RUNNING_STATUS
from kama_sdk.core.core.types import ActionStatusDict, KoD
from kama_sdk.model.base.mc import PATCH_KEY
from kama_sdk.utils.logging import lwin, lerr, lwar


class JobProgressWrapper:

  _job: Job

  def __init__(self, job: Job):
    self._job = job

  def get_meta(self) -> Dict:
    return self._job.meta or {}

  @lru_cache
  def get_progress_bundle(self) -> Optional[ActionStatusDict]:
    serialized = self.get_meta().get('progress')
    as_dict = json.loads(serialized) if serialized else None
    return as_dict

  @lru_cache
  def get_result(self) -> Dict:
    return self._job.result

  @lru_cache
  def get_status(self):
    progress_bundle = self.get_progress_bundle()
    expl_status = progress_bundle.get('status') if progress_bundle else None

    if self._job.is_finished or self._job.is_failed:
      backup_status = POS_STATUS if self._job.is_finished else NEG_STATUS

      if progress_bundle:
        if expl_status not in [POS_STATUS, NEG_STATUS]:
          lwar(f"danger done bad action status {expl_status}")
        return expl_status
      return backup_status
    else:
      backup_status = 'running'
      if progress_bundle:
        if not expl_status == RUNNING_STATUS:
          lwar(f"danger running bad action status {expl_status}")
          return expl_status
      return backup_status


def enqueue_action(kod: KoD, patch=None) -> str:
  return enqueue_func(load_and_perform_action, kod, patch)


def enqueue_func(func: Callable, *args, **kwargs) -> str:
  main_queue = Queue(consts.MAIN_WORKER, connection=conn)
  job = main_queue.enqueue(func, *args, **kwargs)
  return job.get_id()


def enqueue_telem_func(func: Callable, *args, **kwargs) -> str:
  telem_queue = Queue(consts.TELEM_WORKER, connection=conn)
  job = telem_queue.enqueue(func, *args, **kwargs)
  return job.get_id()


def find_job(job_id: str) -> Optional[Job]:
  try:
    return Job.fetch(job_id, connection=conn)
  except NoSuchJobError:
    return None


def job_status(job_id: str) -> JobProgressWrapper:
  job = find_job(job_id)
  return JobProgressWrapper(job)


def load_and_perform_action(kod: KoD, patch=None):
  from kama_sdk.model.action.base.action import Action
  down_kwargs = {PATCH_KEY: patch}
  action: Action = Action.inflate(kod, **down_kwargs)
  print("Final action config")
  print(action.get_config())
  try:
    action.run()
    lwin(f"action={action.get_id()} succeeded")
  except Exception as e:
    lerr(f"action={action.get_id()} failed", exc=e)
    return None
