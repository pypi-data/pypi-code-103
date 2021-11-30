from typing import List, Union, Any

from k8kat.res.base.kat_res import KatRes

from kama_sdk.model.base.common import RESOURCE_SELECTOR_KEY
from kama_sdk.utils import utils
from kama_sdk.utils.logging import lwar
from kama_sdk.utils.utils import kres2dict
from kama_sdk.model.supplier.base.supplier import Supplier, SER_NATIVE
from kama_sdk.model.k8s.resource_selector import ResourceSelector


class ResourcesSupplier(Supplier):

  def get_output_spec(self):
    super_value = super().get_output_spec()
    if super_value == 'options_format':
      ser_type = self.get_serializer_type()
      if not ser_type == SER_NATIVE:
        info = f"serializer {ser_type} != {SER_NATIVE}"
        lwar(f"danger using options_format {info}", sig=self.sig())
      return dict(id='name', title='name')
    return super_value

  def get_resource_selector(self) -> ResourceSelector:
    return self.inflate_child(
      ResourceSelector,
      attr=RESOURCE_SELECTOR_KEY
    )

  def _compute(self) -> List[KatRes]:
    selector = self.get_resource_selector()
    result = selector.query_cluster()
    return result

  def do_jq_serialize(self, kr: Union[KatRes, List[KatRes]]) -> Any:
    is_list = utils.is_listy(kr)
    new_value = list(map(kres2dict, kr)) if is_list else kres2dict(kr)
    return super().do_jq_serialize(new_value)
