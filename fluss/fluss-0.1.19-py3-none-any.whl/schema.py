from fluss.graphql.queries.graph import GET_GRAPH
from fluss.diagram import Diagram
from typing import Any, List, Optional
from herre.convenience import GraphQLModel
from typing import ForwardRef
from enum import Enum
from fluss.ward import FlussWard

Graph = ForwardRef("Graph")


class RepresentationVariety(str, Enum):
    VOXEL = "VOXEL"
    MASK = "MASK"
    UNKNOWN = "UNKNOWN"


class Graph(GraphQLModel):
    template: Optional[str]
    version: Optional[str]
    name: Optional[str]
    diagram: Optional[Diagram]

    class Meta:
        identifier = "graph"
        ward = "fluss"
        get = GET_GRAPH


Graph.update_forward_refs()
