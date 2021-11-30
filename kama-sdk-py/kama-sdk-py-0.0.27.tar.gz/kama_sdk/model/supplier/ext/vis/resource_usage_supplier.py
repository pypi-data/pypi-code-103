from typing import List, Dict

from k8kat.res.base.kat_res import KatRes

from kama_sdk.model.base.common import RESOURCE_SELECTORS_KEY
from kama_sdk.model.k8s.resource_selector import ResourceSelector
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.utils.utils import flatten


class ResourceUsageSupplier(Supplier):

  def get_resource_selectors(self) -> List[ResourceSelector]:
    return self.inflate_children(
      ResourceSelector,
      attr=RESOURCE_SELECTORS_KEY
    )

  def get_workloads(self) -> List[KatRes]:
    if explicit := self.get_attr(WORKLOADS_KEY):
      if isinstance(explicit, list):
        return explicit
      else:
        return [explicit]
    else:
      selectors = self.get_resource_selectors()
      return flatten([s.query_cluster() for s in selectors])

  def get_metric_type(self) -> str:
    return self.get_attr(METRIC_TYPE) or TYPE_MEM

  def get_upper_bound_type(self):
    return self.get_attr(UPPER_BOUND_TYPE_KEY)

  def _compute(self) -> Dict:

    workloads = self.get_workloads()
    metric_type = self.get_metric_type()
    upper_bound_type = self.get_upper_bound_type()
    total_used = compute_total_used(workloads, metric_type)
    upper_bound = compute_upper_bound(workloads, upper_bound_type)

    if upper_bound and upper_bound == 0:
      upper_bound = None

    fraction_used = total_used / upper_bound if upper_bound else None
    pct_used = int(fraction_used * 100) if upper_bound else None

    return {
      'usage': total_used,
      'upper_bound': upper_bound,
      'fraction_used': fraction_used,
      'pct_used': pct_used
    }


def compute_total_used(workloads: List[KatRes], metric_type: str) -> float:
  total_used = 0
  if metric_type == TYPE_MEM:
    total_used = sum([w.mem_used() for w in workloads])
  elif metric_type == TYPE_CPU:
    total_used = sum([w.cpu_used() for w in workloads])
  return total_used


def compute_upper_bound(workloads: List[KatRes], ubt: str) -> float:
  if ubt == 'cpu_limit':
    return sum([w.pods_cpu_limit() for w in workloads])
  elif ubt == 'memory_limit':
    return sum([w.pods_mem_limit() for w in workloads])
  elif ubt == 'cpu_request':
    return sum([w.pods_cpu_request() for w in workloads])
  elif ubt == 'memory_request':
    return sum([w.pods_mem_request() for w in workloads])


METRIC_TYPE = "metric_type"
WORKLOADS_KEY = "workloads"
UPPER_BOUND_TYPE_KEY = "upper_bound_type"
TYPE_CPU = "cpu"
TYPE_MEM = "memory"
