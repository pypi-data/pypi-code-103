from typing import List

from kama_sdk.model.base.model import Model
from kama_sdk.model.view.view_spec import ViewSpec


class ViewGroup(Model):

  def get_view_mode(self) -> str:
    return self.get_local_attr(VIEW_MODE_KEY) or "free"

  def get_collection_specs(self) -> List[ViewSpec]:
    return self.inflate_children(
      ViewSpec,
      attr=COLLECTION_SPECS_KEY
    )


COLLECTION_SPECS_KEY = "collection_specs"
VIEW_MODE_KEY = "mode"
