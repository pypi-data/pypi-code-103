from typing import TYPE_CHECKING, List, Optional

from myst.client import get_client
from myst.connectors.operation_connector import OperationConnector
from myst.models.types import ItemOrSlice, UUIDOrStr, to_uuid
from myst.openapi.api.operations import create_operation, get_operation, list_operation_inputs
from myst.openapi.models.operation_create import OperationCreate
from myst.resources.connector_node import ConnectorNode
from myst.resources.input import Input
from myst.resources.time_series import TimeSeries

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.project import Project


class Operation(ConnectorNode):
    """A node that performs a specified transformation on its input.

    In contrast to a model, an operation has no training phase and can only be run.
    """

    @classmethod
    def create(
        cls, project: "Project", title: str, connector: OperationConnector, description: Optional[str] = None
    ) -> "Operation":
        """Creates a new operation node.

        Args:
            project: the project in which to create the operation
            title: the title of the operation
            connector: the operation connector to use in the operation node
            description: a brief description of the operation

        Returns:
            the newly created operation
        """
        operation = create_operation.request_sync(
            client=get_client(),
            json_body=OperationCreate(
                object="Node",
                type="Operation",
                title=title,
                description=description,
                project=str(project.uuid),
                connector_uuid=str(connector.uuid),
                parameters=connector.parameters_exclude_none(),
            ),
        )

        return Operation.parse_obj(operation.dict())

    @classmethod
    def get(cls, uuid: UUIDOrStr) -> "Operation":
        """Gets a specific operation by its identifier."""
        operation = get_operation.request_sync(client=get_client(), uuid=str(to_uuid(uuid)))

        return Operation.parse_obj(operation.dict())

    def create_input(
        self,
        upstream_node: TimeSeries,
        group_name: str,
        output_index: int = 0,
        label_indexer: Optional[ItemOrSlice] = None,
    ) -> Input:
        """Creates an input into this operation.

        Args:
            upstream_node: the time series to feed into this operation
            group_name: the name of the input group on this operation's connector to which to pass the data from this
                input
            output_index: which time dataset, out of the sequence of upstream time datasets, to pass to this operation
            label_indexer: the slice of the upstream data to pass to this operation

        Returns:
            the newly created input
        """
        return Input.create(
            downstream_node=self,
            upstream_node=upstream_node,
            group_name=group_name,
            output_index=output_index,
            label_indexer=label_indexer,
        )

    def list_inputs(self) -> List[Input]:
        """Lists all inputs into this operation."""
        operation_inputs = list_operation_inputs.request_sync(client=get_client(), operation_uuid=str(self.uuid))

        return [Input.parse_obj(input_.dict()) for input_ in operation_inputs.data]
