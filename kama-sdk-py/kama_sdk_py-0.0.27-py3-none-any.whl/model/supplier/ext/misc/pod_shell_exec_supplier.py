from typing import Any, Optional

from k8kat.res.pod.kat_pod import KatPod
from kama_sdk.model.supplier.base.supplier import Supplier


class PodShellExecOutputSupplier(Supplier):

  def pod(self) -> Optional[KatPod]:
    result = self.get_attr(POD_KEY)
    if isinstance(result, KatPod):
      return result
    else:
      return None

  def command(self):
    return self.get_attr(CMD_KEY, '')

  def _compute(self) -> Any:
    if pod := self.pod():
      command = self.command()
      result = pod.shell_exec(command)
      return result


POD_KEY = "pod"
CMD_KEY = 'command'
