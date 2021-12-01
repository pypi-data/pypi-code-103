from typing import List

from k8kat.res.base.kat_res import KatRes
from k8kat.res.pod.kat_pod import KatPod
from werkzeug.utils import cached_property

from kama_sdk.core.core.types import PodStatusSummary
from kama_sdk.model.supplier.base.supplier import Supplier


class PodStatusSummariesSupplier(Supplier):

  @cached_property
  def workload(self) -> KatRes:
    return self.get_source_data()

  @cached_property
  def pods(self) -> List[KatPod]:
    return self.workload.pods()

  def resolve(self) -> List[PodStatusSummary]:
    return list(map(pod_mini_status, self.pods))


def pod_mini_status(pod: KatPod) -> PodStatusSummary:
  return PodStatusSummary(
    ternary_status=pod.ternary_status(),
    pod_name=pod.name,
    phase=pod.phase
  )
