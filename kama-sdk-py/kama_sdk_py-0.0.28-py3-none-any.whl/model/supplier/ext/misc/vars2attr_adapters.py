from typing import Any, List, Dict

from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.model.variable.manifest_variable import ManifestVariable


class Vars2AttrAdaptersSupplier(Supplier):

  def variables(self) -> List[ManifestVariable]:
    return self.inflate_children(ManifestVariable, attr=VARIABLES_KEY)

  def _compute(self) -> Any:
    return list(map(var2entry, self.variables()))


def var2entry(var: ManifestVariable) -> Dict:
  return dict(
    title=var.get_title(),
    info=var.get_flat_key(),
    value=dict(
      type='View',
      elements=[
        dict(
          type='Text',
          text=var.get_current_value(),
          style=['hacker', 'bold']
        ),
        dict(
          type='Text',
          text=var.get_info(),
          style=['italic', 'calm']
        ),
      ]
    )
  )


VARIABLES_KEY = 'variables'
