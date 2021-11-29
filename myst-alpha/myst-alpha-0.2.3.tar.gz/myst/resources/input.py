from typing import TYPE_CHECKING, Optional, Union

from myst.client import Client, get_client
from myst.models.types import ItemOrSlice
from myst.openapi.api.models import create_model_input
from myst.openapi.api.operations import create_operation_input
from myst.openapi.models.input_create import InputCreate
from myst.openapi.models.input_get import InputGet
from myst.resources.edge import Edge
from myst.resources.time_series import TimeSeries

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.model import Model
    from myst.resources.operation import Operation


def _create_input(downstream_node: Union["Model", "Operation"], input_create: InputCreate, client: Client) -> InputGet:
    from myst.resources.model import Model  # Avoid circular imports.

    if isinstance(downstream_node, Model):
        return create_model_input.request_sync(
            client=client, model_uuid=str(downstream_node.uuid), json_body=input_create
        )
    else:  # i.e. `to` is an `Operation`
        return create_operation_input.request_sync(
            client=client, operation_uuid=str(downstream_node.uuid), json_body=input_create
        )


class Input(Edge):
    """An edge from a time series into a model or operation."""

    @classmethod
    def create(
        cls,
        downstream_node: Union["Model", "Operation"],
        upstream_node: TimeSeries,
        group_name: str,
        output_index: int = 0,
        label_indexer: Optional[ItemOrSlice] = None,
    ) -> "Input":
        """Creates a new input edge between the given nodes.

        Args:
            downstream_node: the model or operation into which data flows out of this edge
            upstream_node: the time series from which data flows into this edge
            group_name: the name of the group of inputs on the underlying model or operation connector to which to pass
                the data from this input
            output_index: which time dataset, out of the sequence of upstream time datasets, to pass to the downstream
                node
            label_indexer: the slice of the upstream data to pass to the downstream node

        Returns:
            the newly created input
        """
        input_create = InputCreate(
            object="Edge",
            type="Input",
            upstream_node=str(upstream_node.uuid),
            group_name=group_name,
            output_index=output_index,
            label_indexer=label_indexer,
        )

        input_ = _create_input(downstream_node=downstream_node, input_create=input_create, client=get_client())

        return Input.parse_obj(input_.dict())
