from typing import Dict

from cachetools.func import lru_cache
from k8kat.res.pod.kat_pod import KatPod
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.utils import utils
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.base.action_errors import FatalActionError
from werkzeug.utils import cached_property


class PodShellExecAction(Action):

  def get_id(self) -> str:
    return super().get_id() or DEFAULT_ID

  def get_title(self) -> str:
    return super().get_title() or DEFAULT_TITLE

  def get_info(self) -> str:
    return super().get_info() or DEFAULT_INFO

  @lru_cache
  def command(self):
    return self.get_attr(CMD_KEY)

  @model_attr(cached=True)
  def get_pod(self) -> KatPod:
    return self.get_attr(POD_KEY)

  def perform(self) -> Dict:
    if pod := self.get_pod():
      command = self.command()
      # print("FINAL COMMAND")
      # print(command)
      self.add_logs([command])
      result = pod.shell_exec(command)
      logs = utils.clean_log_lines(result)
      self.add_logs(logs)
      return dict(output=result)
    else:
      raise_on_pod_missing()


def raise_on_pod_missing():
  raise FatalActionError({
    'type': "no_pod_for_shell_exec",
    'reason': "Command could not be run as pod does not exist"
  })


POD_KEY = "pod"
CMD_KEY = 'command'

DEFAULT_ID = "sdk.action.pod_shell_exec"
DEFAULT_TITLE = "Execute a command in shell pod"
DEFAULT_INFO = "Execute a command in shell pod"
