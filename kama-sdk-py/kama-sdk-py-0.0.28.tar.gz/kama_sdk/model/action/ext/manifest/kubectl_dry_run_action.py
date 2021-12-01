from typing import Dict, List, Optional

from kama_sdk.core.core.types import ErrorCapture
from kama_sdk.core.ktea.ktea_client import KteaClient
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.base.action_errors import FatalActionError
from kama_sdk.model.base.mc import TITLE_KEY, INFO_KEY


class KubectlDryRunAction(Action):
  """
  Serves to hit the breaks in a sequence of actions if `kubectl apply`
  rejects the Kubernetes resource descriptors (given by
  `res_descs: List[Dict]`) that we give it.
  """

  def get_title(self) -> Optional[str]:
    return self.get_local_attr(TITLE_KEY) or DEFAULT_TITLE

  def get_info(self) -> Optional[str]:
    return self.get_local_attr(INFO_KEY) or DEFAULT_INFO

  def res_descs(self) -> List[Dict]:
    return self.get_attr(RES_DESCS_KEY, backup=[])

  def perform(self) -> None:
    res_descs = self.res_descs()
    raise_if_res_descs_none(res_descs)
    if len(res_descs) > 0:
      success, logs = KteaClient.kubectl_dry_run(res_descs)
      self.add_logs(logs)
      raise_on_dry_run_err(success, logs)
    else:
      self.add_logs(['WARN zero resources passed to kubectl'])


def raise_on_dry_run_err(success: bool, logs):
  if not success:
    raise FatalActionError(ErrorCapture(
      type='kubectl_dry_run_failed',
      reason='kubectl dry_run failed for one or more resource.',
      logs=logs
    ))


def raise_if_res_descs_none(res_descs: List[Dict]):
  if res_descs is None:
    raise FatalActionError(ErrorCapture(
      type='kubectl_apply',
      reason="res_descs undefined, action does not know what "
             "to pass to kubectl",
      logs=['res_descs undefined']
    ))


RES_DESCS_KEY = "res_descs"
DEFAULT_TITLE = "Run kubectl dry run"
DEFAULT_INFO = "Ensure API server accepts incoming manifest"
