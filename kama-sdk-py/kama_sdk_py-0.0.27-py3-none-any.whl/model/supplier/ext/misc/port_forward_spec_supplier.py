from typing import Optional

from k8kat.res.svc.kat_svc import KatSvc
from kubernetes.client import V1EndpointAddress, V1ObjectReference

from kama_sdk.utils import utils
from kama_sdk.core.core.types import PortForwardSpec
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.supplier.base.supplier import Supplier


class PortForwardSpecSupplier(Supplier):

  @model_attr()
  def get_kat_svc(self) -> Optional[KatSvc]:
    result = self.get_attr(SVC_KEY)
    if isinstance(result, KatSvc):
      return result
    else:
      return None

  @model_attr()
  def get_explicit_port(self):
    return self.get_attr(PORT_KEY)

  @model_attr()
  def spec(self) -> Optional[PortForwardSpec]:
    svc = self.get_kat_svc()
    winner = None
    backend_dicts = svc.flat_endpoints() or []
    for backend_dict in utils.compact(backend_dicts):
      address: V1EndpointAddress = backend_dict
      target_ref: V1ObjectReference = address.target_ref
      if target_ref and target_ref.kind == 'Pod':
        winner = target_ref
        break

    if winner:
      explicit_port = self.get_explicit_port()
      backup_port = svc.first_tcp_port_num()
      return PortForwardSpec(
        namespace=winner.namespace,
        pod_name=winner.name,
        pod_port=int(explicit_port or backup_port or '80')
      )

  @model_attr()
  def get_pod_port(self):
    return self.spec().get('pod_port') if self.spec() else ''

  def _compute(self) -> Optional[PortForwardSpec]:
    return self.spec()


SVC_KEY = 'svc'
PORT_KEY = 'port'
