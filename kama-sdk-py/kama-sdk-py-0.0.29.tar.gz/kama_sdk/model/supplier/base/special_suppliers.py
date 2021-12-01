from typing import Optional, Any

from kama_sdk.model.base.model import Model
from kama_sdk.model.supplier.base import supplier
from kama_sdk.model.supplier.base.supplier import Supplier


class ModelSupplier(Supplier):
  """
  Parent class for reflexive suppliers, e.g that use a Model
  instance as their input.
  """
  pass


class SelfSupplier(ModelSupplier):
  """
  For reflexively accessing own properties. Makes its data source
  its parent (rather than literally self) so that `output` queries
  the model of interest. The `serializer` should only be 'attr'.
  """
  def get_source_data(self) -> Optional[Any]:
    """
    Use parent because that's what the caller cares about. Self
    is likely trivial.
    :return:
    """
    return self.get_parent()


class ParentSupplier(ModelSupplier):
  """
  For reflexively accessing own properties. Makes its data source
  its parent (rather than literally self) so that `output` queries
  the model of interest. The `serializer` should only be 'attr'.
  """
  def get_source_data(self) -> Optional[Any]:
    """
    Use parent because that's what the caller cares about. Self
    is likely trivial.
    :return:
    """
    return self.get_parent().get_parent()


class DelayedInflateSupplier(ModelSupplier):
  """
  Given an id reference to another Model, inflates and returns
  the Model at computation time so that `output` can be used against
  it.
  """
  def get_source_data(self) -> Optional[Any]:
    """
    Override uses get_config() to ensure no special resolution
    happens on the input.
    :return:
    """
    return self.get_config().get(supplier.SRC_DATA_KEY)

  def _compute(self) -> Model:
    source = self.get_source_data()
    return self.inflate_child(Model, kod=source, safely=True)
