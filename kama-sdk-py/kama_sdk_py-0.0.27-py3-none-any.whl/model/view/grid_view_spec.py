from typing import List, Dict, Optional

from kama_sdk.model.base.common import TYPE_KEY
from kama_sdk.model.view.view_spec import ViewSpec, SPEC_KEY
from kama_sdk.serializers.common_serializers import ser_meta
from kama_sdk.utils.logging import lwar


def ser_cell_meta(meta: ViewSpec) -> Dict:
  unresolved_spec = meta.get_config().get(SPEC_KEY)
  width, height = None, None
  if isinstance(unresolved_spec, dict):
    width = unresolved_spec.get('width')
    height = unresolved_spec.get('height')
  return {**ser_meta(meta), 'width': width, 'height': height}


class GridViewSpec(ViewSpec):

  def get_cell_specs(self) -> List[ViewSpec]:
    return self.inflate_children(ViewSpec, attr=CELLS_SPEC_KEY)

  def compute_spec(self) -> Dict:
    cell_spec_metas = list(map(ser_cell_meta, self.get_cell_specs()))

    return {
      **ser_meta(self),
      TYPE_KEY: self.get_view_type(),
      'cell_spec_metas': cell_spec_metas
    }

  def find_cell_spec(self, cell_id: str) -> Optional[ViewSpec]:
    spec_models = self.get_cell_specs()
    finder = lambda m: m.get_id() == cell_id
    return next(filter(finder, spec_models), None)

  def compute_cell_view_spec(self, cell_id: str) -> Dict:
    if spec_model := self.find_cell_spec(cell_id):
      return spec_model.compute_spec()
    else:
      lwar(f"no cell {cell_id}", sig=self.sig())
      return {}

  def get_view_type(self):
    return self.get_local_attr(DISPLAY_TYPE_KEY) or "grid"


CELLS_SPEC_KEY = "cell_specs"
DISPLAY_TYPE_KEY = "display"
