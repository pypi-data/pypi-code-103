from typing import List, Optional, Dict

import yaml
from typing_extensions import TypedDict

from kama_sdk.core.core.types import K8sResDict, KteaDict, ErrorCapture
from kama_sdk.core.ktea import ktea_provider
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.base.action_errors import FatalActionError
from kama_sdk.model.base.common import VALUES_KEY
from kama_sdk.model.base.mc import TITLE_KEY, INFO_KEY
from kama_sdk.model.k8s.resource_selector import ResourceSelector


MaybeResDescs = Optional[List[K8sResDict]]


class OutputFormat(TypedDict):
  res_descs: List[K8sResDict]


class TemplateManifestAction(Action):

  def get_id(self) -> str:
    return super().get_id() or "sdk.action.template_manifest"

  def get_title(self) -> Optional[str]:
    return self.get_local_attr(TITLE_KEY) or DEFAULT_TITLE

  def get_info(self) -> Optional[str]:
    return self.get_local_attr(INFO_KEY) or DEFAULT_INFO

  def get_ktea_config(self) -> KteaDict:
    return self.get_attr(KTEA_KEY)

  def get_values(self) -> Dict:
    return self.get_attr(VALUES_KEY, depth=100)

  def get_resource_selectors(self) -> List[ResourceSelector]:
    return self.inflate_children(ResourceSelector, attr=RES_WHITELIST_KEY)

  def perform(self) -> OutputFormat:
    ktea = self.get_ktea_config()
    values = self.get_values()
    selectors = self.get_resource_selectors()

    # print({
    #   'ktea': ktea,
    #   'values': values,
    #   'selectors': selectors
    # })

    client_inst = ktea_provider.ktea_client(
      ktea=ktea,
      space=self.get_config_space()
    )
    res_descs = client_inst.template_manifest(values)

    scan_and_raise(ktea, res_descs)
    self.add_logs(list(map(yaml.dump, res_descs)))

    filtered_descs = client_inst.filter_res(res_descs, selectors)
    return dict(res_descs=filtered_descs)


def scan_and_raise(ktea: KteaDict, res_descs: MaybeResDescs):
  if res_descs is None:
    ktea_type = ktea.get('type') if ktea else None
    ktea_name = ktea.get('uri') if ktea else None
    ktea_sig = f"{ktea_type or '[no type]'}/{ktea_name or '[no uri]'}"
    raise FatalActionError(ErrorCapture(
      type='template_manifest_failed',
      reason=f"Templating engine {ktea_sig} returned no data",
      extras=dict(ktea=ktea)
    ))


KTEA_KEY = 'ktea'
RES_WHITELIST_KEY = 'resource_whitelist_selectors'
OUT_RES_DESCS_KEY = 'res_descs'

DEFAULT_TITLE = "Load Templated Manifest"
DEFAULT_INFO = "Invoke publisher-supplied KTEA server, workload, or executable"
