from functools import singledispatch
from typing import List, Optional, Union

from myst.client import get_client
from myst.connectors.model_connector import ModelConnector
from myst.connectors.operation_connector import OperationConnector
from myst.connectors.source_connector import SourceConnector
from myst.core.time.time_delta import TimeDelta
from myst.models.types import AxisLabels, CoordinateLabels, Shape, UUIDOrStr, to_uuid
from myst.openapi.api.projects import create_project, get_project, list_project_edges, list_project_nodes, list_projects
from myst.openapi.models.deploy_status import DeployStatus
from myst.openapi.models.input_get import InputGet
from myst.openapi.models.layer_get import LayerGet
from myst.openapi.models.model_get import ModelGet
from myst.openapi.models.operation_get import OperationGet
from myst.openapi.models.project_create import ProjectCreate
from myst.openapi.models.source_get import SourceGet
from myst.openapi.models.time_series_get import TimeSeriesGet
from myst.resources.edge import Edge
from myst.resources.input import Input
from myst.resources.layer import Layer
from myst.resources.model import Model
from myst.resources.node import Node
from myst.resources.operation import Operation
from myst.resources.resource import ShareableResource
from myst.resources.source import Source
from myst.resources.time_series import TimeSeries


@singledispatch
def _parse_node(node: Union[TimeSeriesGet, SourceGet, OperationGet, ModelGet]) -> Node:
    raise NotImplementedError()


@_parse_node.register
def _parse_time_series(node: TimeSeriesGet) -> TimeSeries:
    return TimeSeries.parse_obj(node.dict())


@_parse_node.register
def _parse_source(node: SourceGet) -> Source:
    return Source.parse_obj(node.dict())


@_parse_node.register
def _parse_model(node: ModelGet) -> Model:
    return Model.parse_obj(node.dict())


@_parse_node.register
def _parse_operation(node: OperationGet) -> Operation:
    return Operation.parse_obj(node.dict())


@singledispatch
def _parse_edge(node: Union[InputGet, LayerGet]) -> Edge:
    raise NotImplementedError()


@_parse_edge.register
def _parse_input(edge: InputGet) -> Input:
    return Input.parse_obj(edge.dict())


@_parse_edge.register
def _parse_layer(edge: LayerGet) -> Layer:
    return Layer.parse_obj(edge.dict())


class Project(ShareableResource):
    """A workspace for creating and deploying graphs of time series.

    A project collects the nodes and edges of the graph along with any policies used to execute the graph.
    """

    title: str
    deploy_status: DeployStatus
    description: Optional[str] = None

    @classmethod
    def create(cls, title: str, description: Optional[str] = None) -> "Project":
        """Creates a new project.

        Args:
            title: the title of the project
            description: a brief description of the project

        Returns:
            the newly created project
        """
        project = create_project.request_sync(
            client=get_client(), json_body=ProjectCreate(object="Project", title=title, description=description)
        )

        return Project.parse_obj(project.dict())

    @classmethod
    def list(cls) -> List["Project"]:
        """Lists all projects visible to the user."""
        projects = list_projects.request_sync(client=get_client())

        return [Project.parse_obj(project.dict()) for project in projects.data]

    @classmethod
    def get(cls, uuid: UUIDOrStr) -> "Project":
        """Gets a specific project by its identifier."""
        project = get_project.request_sync(client=get_client(), uuid=str(to_uuid(uuid)))

        return Project.parse_obj(project.dict())

    def list_nodes(self) -> List[Node]:
        """Lists all nodes in this project."""
        project_nodes = list_project_nodes.request_sync(client=get_client(), project_uuid=str(self.uuid))

        return [_parse_node(node) for node in project_nodes.data]

    def list_edges(self) -> List[Edge]:
        """Lists all edges in this project."""
        project_edges = list_project_edges.request_sync(client=get_client(), project_uuid=str(self.uuid))

        return [_parse_edge(edge) for edge in project_edges.data]

    def create_source(self, title: str, connector: SourceConnector, description: Optional[str] = None) -> Source:
        """Creates a new source node in this project.

        Args:
            title: the title of the source
            connector: specification of the connector this source should use
            description: a brief description of the source

        Returns:
            the newly created source
        """
        return Source.create(project=self, title=title, connector=connector, description=description)

    def create_model(self, title: str, connector: ModelConnector, description: Optional[str] = None) -> Model:
        """Creates a new model node in this project.

        Args:
            title: the title of the model
            connector: specification of the connector this model should use
            description: a brief description of the model

        Returns:
            the newly created model
        """
        return Model.create(project=self, title=title, connector=connector, description=description)

    def create_operation(
        self, title: str, connector: OperationConnector, description: Optional[str] = None
    ) -> Operation:
        """Creates a new operation node in this project.

        Args:
            title: the title of the operation
            connector: specification of the connector this operation should use
            description: a brief description of the operation

        Returns:
            the newly created operation
        """
        return Operation.create(project=self, title=title, connector=connector, description=description)

    def create_time_series(
        self,
        title: str,
        sample_period: TimeDelta,
        cell_shape: Shape = (),
        coordinate_labels: CoordinateLabels = (),
        axis_labels: AxisLabels = (),
        description: Optional[str] = None,
    ) -> TimeSeries:
        """Creates a new time series node in this project.

        Args:
            title: the title of the time series
            sample_period: the frequency at which the data is sampled
            cell_shape: the shape of the data in each cell of the time series
            coordinate_labels: the labels for each coordinate of a cell in the time series
            axis_labels: the labels for each axis of a cell in the time series
            description: a brief description of the time series

        Returns:
            the newly created time series
        """
        return TimeSeries.create(
            project=self,
            title=title,
            sample_period=sample_period,
            cell_shape=cell_shape,
            coordinate_labels=coordinate_labels,
            axis_labels=axis_labels,
            description=description,
        )
