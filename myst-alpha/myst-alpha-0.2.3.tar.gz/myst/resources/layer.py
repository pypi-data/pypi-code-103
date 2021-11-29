from typing import TYPE_CHECKING, Optional

from myst.adapters.timing import to_timing_create
from myst.client import get_client
from myst.models.timing import AbsoluteOrRelativeTiming, TimeRangeBoundary, from_time_range_boundary
from myst.models.types import ItemOrSlice
from myst.openapi.api.time_series import create_time_series_layer
from myst.openapi.models.layer_create import LayerCreate
from myst.resources.edge import Edge
from myst.resources.node import Node

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.time_series import TimeSeries


class Layer(Edge):
    """An edge into a time series.

    Layers are a way of stitching together data from multiple upstream nodes into a single, cohesive time series. Data
    can be combined across different time ranges, and a time series can use data from a lower-precedence layer when
    data is missing from a higher-precedence layer.

    Attributes:
        order: integer specifying priority of this layer when combining multiple layers; lower order implies higher
            precedence
        start_timing: the beginning of the natural time range this layer should produce data for; if None, there is no
            restriction on the beginning of the range
        end_timing: the end of the natural time range this layer should produce data for; if None, there is no
            restriction on the end of the range
    """

    order: int
    start_timing: Optional[AbsoluteOrRelativeTiming] = None
    end_timing: Optional[AbsoluteOrRelativeTiming] = None

    @classmethod
    def create(
        cls,
        downstream_node: "TimeSeries",
        upstream_node: Node,
        order: int,
        output_index: int = 0,
        label_indexer: Optional[ItemOrSlice] = None,
        start_timing: Optional[TimeRangeBoundary] = None,
        end_timing: Optional[TimeRangeBoundary] = None,
    ) -> "Layer":
        layer = create_time_series_layer.request_sync(
            client=get_client(),
            time_series_uuid=str(downstream_node.uuid),
            json_body=LayerCreate(
                object="Edge",
                type="Layer",
                upstream_node=str(upstream_node.uuid),
                order=order,
                output_index=output_index,
                label_indexer=label_indexer,
                start_timing=to_timing_create(from_time_range_boundary(start_timing)),
                end_timing=to_timing_create(from_time_range_boundary(end_timing)),
            ),
        )

        return Layer.parse_obj(layer.dict())
