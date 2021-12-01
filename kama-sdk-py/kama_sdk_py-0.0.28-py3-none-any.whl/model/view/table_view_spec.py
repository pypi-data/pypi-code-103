from typing import List, Dict

from kama_sdk.model.base.common import DATA_KEY, TYPE_KEY
from kama_sdk.model.view.column_spec import ColumnSpec
from kama_sdk.model.view.view_spec import ViewSpec
from kama_sdk.serializers.common_serializers import ser_meta


class TableViewSpec(ViewSpec):

  def get_column_specs(self) -> List[ColumnSpec]:
    return self.inflate_children(ColumnSpec, attr=COLUMNS_KEY)

  def compute_spec(self) -> Dict:
    col_spec_metas = list(map(ser_meta, self.get_column_specs()))
    return {
      **ser_meta(self),
      TYPE_KEY: "table",
      'column_metas': col_spec_metas
    }

  def get_data(self) -> List:
    return self.get_typed_attr(DATA_KEY, List, alt=[])

  def compute_frame_view_specs(self) -> List[Dict]:
    column_specs = self.get_column_specs()
    data = self.get_data()
    frames = []
    for item in data:
      frame = {}
      for column_spec in column_specs:
        view_spec_model = column_spec.get_primed_view_spec(item)
        spec = view_spec_model.compute_spec()
        frame[column_spec.get_key()] = spec
      frames.append(frame)
    return frames

  @classmethod
  def get_view_type(cls):
    return "table"


COLUMNS_KEY = "column_specs"
