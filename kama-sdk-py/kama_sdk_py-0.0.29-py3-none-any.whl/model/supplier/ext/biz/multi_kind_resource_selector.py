from typing import List

from k8kat.res.base.kat_res import KatRes
from werkzeug.utils import cached_property

from kama_sdk.model.k8s.resource_selector import ResourceSelector, FIELD_SEL_KEY, NOT_LABEL_SEL_KEY, LABEL_SEL_KEY, \
  RES_NAME_KEY, RES_NS_KEY, RES_KIND_KEY


class MultiKindResourceSelector(ResourceSelector):

  @cached_property
  def res_kinds(self) -> List[str]:
    return self.get_attr(RES_KINDS_KEY) or []

  def query_cluster(self) -> List[KatRes]:
    results = []
    for res_kind in self.get_res_kind():
      selector = self.synthesize_single_kind_sel(res_kind)
      results.extend(selector.query_cluster())
    return results

  def synthesize_single_kind_sel(self, res_kind: str) -> ResourceSelector:
    synth_descriptor = {
      RES_KIND_KEY: res_kind,
      RES_NS_KEY: self.get_res_ns(),
      RES_NAME_KEY: self.get_res_name(),
      LABEL_SEL_KEY: self.get_label_selector(),
      NOT_LABEL_SEL_KEY: self.get_not_label_selector(),
      FIELD_SEL_KEY: self.get_field_selector()
    }

    return self.inflate_child(
      ResourceSelector,
      kod=synth_descriptor
    )


RES_KINDS_KEY = 'res_kinds'
