from functools import lru_cache
from typing import List, Optional, Dict

from k8kat.res.ingress.kat_ingress import KatIngress
from k8kat.res.svc.kat_svc import KatSvc

from kama_sdk.core.core import structured_search
from kama_sdk.core.core.types import PortForwardSpec
from kama_sdk.model.base.common import PREDICATES_KEY
from kama_sdk.model.base.model import Model
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.model.k8s.resource_selector import ResourceSelector
from kama_sdk.model.supplier.ext.misc import port_forward_spec_supplier
from kama_sdk.model.supplier.ext.misc.port_forward_spec_supplier import PortForwardSpecSupplier
from kama_sdk.model.predicate.predicate import Predicate

class SiteEndpoint(Model):

  def source_type(self) -> Optional[str]:
    return self.get_attr('type', lookback=False)

  def url(self) -> Optional[str]:
    return self.get_local_attr('url')

  def is_enabled(self) -> bool:
    return self.get_local_attr('enabled')

  def is_ingress(self) -> bool:
    return self.source_type() == 'Ingress'

  def is_load_balancer(self) -> bool:
    return self.source_type() == 'LoadBalancer'

  def is_node_port(self) -> bool:
    return self.source_type() == 'NodePort'

  def is_cluster_ip(self) -> bool:
    return self.source_type() == 'ClusterIP'

  def port_forward_spec(self) -> Optional[PortForwardSpec]:
    return self.get_local_attr('port_forward_spec')

  def bundle(self):
    return {
      'type': self.source_type(),
      'url': self.url(),
      'port_forward_spec': self.port_forward_spec(),
      'enabled': self.is_enabled()
    }


class SiteAccessNode(Model):
  def predicates(self) -> List[Predicate]:
    return self.inflate_children(
      Predicate,
      attr=PREDICATES_KEY,
      resolve_kod=False
    )

  def predicate_kods(self):
    return self._config.get("predicates") or []

  def endpoints(self) -> List[SiteEndpoint]:
    return self.inflate_children(SiteEndpoint, attr='endpoints')


class AccessNodeSerializer(Supplier):

  def get_node(self) -> SiteAccessNode:
    return self.inflate_child(SiteAccessNode, attr="access_node", safely=True)

  def _compute(self) -> List:
    node = self.get_node()
    endpoint_urls = [e.url() for e in node.endpoints()] if node else []
    return endpoint_urls


class SiteAccessNodesSerializer(Supplier):

  @lru_cache
  def nodes(self) -> List[SiteAccessNode]:
    return self.inflate_children(SiteAccessNode, attr="site_access_nodes")

  def _compute(self):
    output = []
    for node in self.nodes():
      endpoints = node.endpoints()
      output.append({
        'title': node.get_title(),
        'predicates': node.predicate_kods(),
        'endpoints': [e.bundle() for e in endpoints]
      })
    return output


class SimpleIngressSiteAccessNode(SiteAccessNode):

  def get_title(self):
    explicit = super(SimpleIngressSiteAccessNode, self).get_title()
    return explicit or "External Ingress"

  def ingress_selector(self) -> Optional[ResourceSelector]:
    return self.inflate_child(
      ResourceSelector,
      attr='ingress_selector',
      safely=True
    )

  def get_ingress_resource(self) -> Optional[KatIngress]:
    if selector := self.ingress_selector():
      result = selector.query_cluster()
      return next(iter(result), None)
    else:
      return None

  def rule_matcher(self) -> Dict:
    value = self.get_attr('match', lookback=False)
    return value if isinstance(value, Dict) else {}

  def endpoints(self) -> List[SiteEndpoint]:
    if ingress := self.get_ingress_resource():
      rule_dicts = ingress.flat_rules()
      matcher = self.rule_matcher()
      final_rules = structured_search.query(matcher, rule_dicts)
      configs = list(map(ingress_rule_2_endpoint_config, final_rules))
      return self.inflate_children(SiteEndpoint, kod=configs)
    else:
      return []


class SimpleServiceSiteAccessNode(SiteAccessNode):

  def get_title(self):
    explicit = super(SimpleServiceSiteAccessNode, self).get_title()
    return explicit or "Standard Service"

  def service_selector(self) -> Optional[ResourceSelector]:
    return self.inflate_child(
      ResourceSelector,
      attr='service_selector',
      safely=True
    )

  @lru_cache
  def service(self) -> Optional[KatSvc]:
    if explicit := self.get_attr("service"):
      return explicit
    else:
      if selector := self.service_selector():
        result = selector.query_cluster()
        return next(iter(result), None)
      else:
        return None

  def service_type(self):
    return self.service().type if self.service() else None

  def load_balancer_endpoint(self) -> SiteEndpoint:
    return self.inflate_child(SiteEndpoint, kod={
      'kind': SiteEndpoint.__name__,
      'type': 'LoadBalancer',
      'enabled': self.service_type() == 'LoadBalancer',
      'url': self.service().external_ip if self.service() else None
    })

  def node_port_endpoint(self) -> SiteEndpoint:
    return self.inflate_child(SiteEndpoint, kod={
      'kind': SiteEndpoint.__name__,
      'type': 'NodePort',
      'enabled': self.service_type() == 'NodePort',
      'url': self.service().external_ip if self.service() else None
    })

  def internal_endpoint(self) -> SiteEndpoint:
    spec = None
    if self.service():
      supplier = PortForwardSpecSupplier({
        port_forward_spec_supplier.SVC_KEY: self.service()
      })
      spec = supplier.resolve()

    return self.inflate_child(SiteEndpoint, kod={
      'kind': SiteEndpoint.__name__,
      'type': 'ClusterIP',
      'url': self.service().internal_ip if self.service() else None,
      'port_forward_spec': spec,
      'enabled': True
    })

  def endpoints(self) -> List[SiteEndpoint]:
    return [
      self.internal_endpoint(),
      self.load_balancer_endpoint(),
      self.node_port_endpoint()
    ]


# class ConvenientSiteAccessNode(SiteAccessNode):
#
#   def endpoints(self) -> List[SiteEndpoint]:
#     service_node = SimpleServiceSiteAccessNode(self.get_config())
#     ingress_node = SimpleIngressSiteAccessNode(self.get_config())
#
#     pass

class BestSiteEndpointSupplier(Supplier):

  def site_access_nodes(self) -> List[SiteAccessNode]:
    return self.inflate_children(SiteAccessNode, attr='site_access_nodes')

  @lru_cache
  def best_endpoint(self) -> Optional[SiteEndpoint]:
    winner: Optional[SiteEndpoint] = None
    for node in self.site_access_nodes():
      for endpoint in node.endpoints():
        if endpoint.is_ingress() and endpoint.is_enabled():
          return endpoint
        if winner is not None:
          winner = endpoint_compare(winner, endpoint)
        else:
          winner = endpoint
    return winner

  @lru_cache
  def bundle(self) -> Dict:
    endpoint = self.best_endpoint()
    return endpoint.bundle() if endpoint else None

  def _compute(self) -> Optional[Dict]:
    return self.bundle()

  @model_attr()
  def action_descriptor(self):
    if result := self.best_endpoint():
      if result.is_cluster_ip():
        return {'type': 'port_forward', 'uri': result.url()}
      else:
        return {'type': 'www', 'uri': result.url()}
    else:
      return None

  @model_attr(key='url')
  def as_url(self):
    if endpoint := self.best_endpoint():
      if endpoint.is_cluster_ip():
        return f"localhost:{endpoint.url().get('pod_port')}"
      else:
        return endpoint.url()
    else:
      return None


def endpoint_compare(ep1: SiteEndpoint, ep2: SiteEndpoint) -> SiteEndpoint:
  if ep1.is_enabled() == ep2.is_enabled():
    if ep1.source_type() == ep2.source_type():
      return ep1
    else:
      ep1_score = std_svc_type_score(ep1.source_type())
      ep2_score = std_svc_type_score(ep2.source_type())
      return ep1 if ep1_score > ep2_score else ep2
  else:
    if ep1.is_enabled() and not ep2.is_enabled():
      return ep1
    elif not ep1.is_enabled() and ep2.is_enabled():
      return ep2


def std_svc_type_score(_type: str) -> int:
  if _type == 'ClusterIP':
    return 0
  elif _type == 'NodePort':
    return 1
  elif _type == 'LoadBalancer':
    return 2
  else:
    return -1


def ingress_rule_2_endpoint_config(rule: Dict) -> Dict:
  host = rule.get("host")
  path = rule.get("path") or ""

  path = "" if str(path) == '/' else path
  url = f"{host}{path}"

  return {
    'type': 'Ingress',
    'enabled': True,
    'url': url
  }
