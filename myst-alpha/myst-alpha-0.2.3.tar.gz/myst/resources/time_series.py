from typing import TYPE_CHECKING, List, Optional, Union

from myst import get_client
from myst.adapters.timing import to_timing_create
from myst.core.data.time_array import TimeArray
from myst.core.time.time import Time
from myst.core.time.time_delta import TimeDelta
from myst.models.time_dataset import TimeDataset, TimeDatasetRow
from myst.models.timing import ScheduleTiming, TimeRangeBoundary, from_schedule_specifier, from_time_range_boundary
from myst.models.types import AxisLabels, CoordinateLabels, ItemOrSlice, Shape, UUIDOrStr, to_uuid
from myst.openapi.api.time_series import (
    create_time_series,
    create_time_series_run_policy,
    get_time_series,
    insert_time_series_data,
    list_time_series_layers,
    list_time_series_run_policies,
    query_time_series_data,
)
from myst.openapi.models.time_series_create import TimeSeriesCreate
from myst.openapi.models.time_series_insert import TimeSeriesInsert
from myst.openapi.models.time_series_run_policy_create import TimeSeriesRunPolicyCreate
from myst.resources.layer import Layer
from myst.resources.node import Node
from myst.resources.policy import TimeSeriesRunPolicy

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.project import Project


class TimeSeries(Node):
    """A queryable, shareable node containing fixed-frequency, arbitrarily dimensioned time series data.

    A time series stitches together data from multiple layers into a single stream, by consuming data from lower-
    precedence layers when data from higher-precedence layers is not available, and by consuming only the upstream data
    that is within the time range bounds set on each layer.

    In addition to queries, a time series also supports inserts, which take precedence over data flowing through the
    input layers.

    Attributes:
        sample_period: the frequency at which the data is sampled
        cell_shape: the shape of the data in each cell
        coordinate_labels: the labels for each coordinate of a cell
        axis_labels: the labels for each axis of a cell
    """

    sample_period: TimeDelta
    cell_shape: Shape
    coordinate_labels: CoordinateLabels
    axis_labels: AxisLabels

    @classmethod
    def create(
        cls,
        project: "Project",
        title: str,
        sample_period: TimeDelta,
        cell_shape: Shape = (),
        coordinate_labels: CoordinateLabels = (),
        axis_labels: AxisLabels = (),
        description: Optional[str] = None,
    ) -> "TimeSeries":
        """Creates a new time series node.

        Args:
            project: the project in which to create the time series
            title: the title of the time series
            sample_period: the frequency at which the data is sampled
            cell_shape: the shape of the data in each cell of the time series
            coordinate_labels: the labels for each coordinate of a cell in the time series
            axis_labels: the labels for each axis of a cell in the time series
            description: a brief description of the time series

        Returns:
            the newly created time series
        """
        time_series = create_time_series.request_sync(
            client=get_client(),
            json_body=TimeSeriesCreate(
                object="Node",
                type="TimeSeries",
                title=title,
                project=str(project.uuid),
                sample_period=sample_period.to_iso_string(),
                cell_shape=cell_shape,
                coordinate_labels=coordinate_labels,
                axis_labels=axis_labels,
                description=description,
            ),
        )

        return TimeSeries.parse_obj(time_series.dict())

    @classmethod
    def get(cls, uuid: UUIDOrStr) -> "TimeSeries":
        """Gets a specific time series by its identifier."""
        time_series = get_time_series.request_sync(client=get_client(), uuid=str(to_uuid(uuid)))

        return TimeSeries.parse_obj(time_series.dict())

    def insert_time_array(self, time_array: TimeArray) -> None:
        """Inserts data from a `TimeArray` into this time series.

        The data from this manual insertion will take precedence over the other layers flowing into this time series.

        Args:
            time_array: the array of data to be inserted
        """
        time_dataset_row = TimeDatasetRow(
            start_time=time_array.start_time,
            end_time=time_array.end_time,
            as_of_time=time_array.as_of_time,
            values=time_array.values,
            mask=time_array.mask,
        )

        time_dataset = TimeDataset(
            object="TimeDataset",
            cell_shape=time_array.cell_shape,
            sample_period=time_array.sample_period,
            data=[time_dataset_row],
            coordinate_labels=time_array.coordinate_labels,
            axis_labels=time_array.axis_labels,
        )

        insert_time_series_data.request_sync(
            client=get_client(), uuid=str(self.uuid), json_body=TimeSeriesInsert(time_dataset=time_dataset)
        )

    def query_time_array(
        self,
        start_time: Time,
        end_time: Time,
        as_of_time: Optional[Time] = None,
        as_of_offset: Optional[TimeDelta] = None,
    ) -> TimeArray:
        """Queries this time series for data according to the given parameters.

        At most one of `as_of_time` and `as_of_offset` may be specified. If `as_of_time` is specified, the query will
        return data as of that particular time. If `as_of_offset` is specified, the query will return data for a
        constant offset between the "natural" time and the as of time. If neither is specified, the API assumes an
        `as_of_time` of now.

        Args:
            start_time: the beginning of the natural time range to query over, inclusive
            end_time: the end of the natural time range to query over, exclusive
            as_of_time: the precise as of time to query
            as_of_offset: the offset from as of time to query by, where as_of_offset = natural_time - as_of_time

        Returns:
            a time array containing data for the specified time range and as of time

        Raises:
            ValueError: if both `as_of_time` and `as_of_offset` are specified
        """
        if as_of_time and as_of_offset:
            raise ValueError("At most one of `as_of_time` and `as_of_offset` may be specified.")

        time_series_query_result_get = query_time_series_data.request_sync(
            client=get_client(),
            uuid=str(self.uuid),
            start_time=start_time.to_iso_string(),
            end_time=end_time.to_iso_string(),
            as_of_time=as_of_time and as_of_time.to_iso_string(),
            as_of_offset=as_of_offset and as_of_offset.to_iso_string(),
        )

        time_dataset = TimeDataset.parse_obj(time_series_query_result_get.time_dataset)

        return time_dataset.flatten()

    def create_layer(
        self,
        upstream_node: Node,
        order: int,
        output_index: int = 0,
        label_indexer: Optional[ItemOrSlice] = None,
        start_timing: Optional[TimeRangeBoundary] = None,
        end_timing: Optional[TimeRangeBoundary] = None,
    ) -> Layer:
        """Creates a layer into this time series.

        Args:
            upstream_node: the node whose data will flow into this time series
            order: integer specifying priority of this layer when combining multiple layers; lower order implies
                higher precedence
            output_index: which time dataset, out of the sequence of upstream time datasets, to pass to this time
                series
            label_indexer: the slice of the upstream data to pass to this time series
            start_timing: the beginning of the natural time range this layer should produce data for; if None, there
                is no restriction on the beginning of the range
            end_timing: the end of the natural time range this layer should produce data for; if None, there is no
                restriction on the end of the range

        Returns:
            the newly created layer
        """
        return Layer.create(
            downstream_node=self,
            upstream_node=upstream_node,
            order=order,
            output_index=output_index,
            label_indexer=label_indexer,
            start_timing=start_timing,
            end_timing=end_timing,
        )

    def list_layers(self) -> List[Layer]:
        """Lists all layers into this time series."""
        time_series_layers = list_time_series_layers.request_sync(client=get_client(), time_series_uuid=str(self.uuid))

        # Parse the layers into their final representation.
        unsorted_layers = [Layer.parse_obj(layer.dict()) for layer in time_series_layers.data]

        # The API returns the layers ordered by create time, descending. We prefer explicit layer ordering here.
        return sorted(unsorted_layers, key=lambda layer: layer.order)

    def create_run_policy(
        self,
        schedule_timing: Union[Time, TimeDelta, ScheduleTiming],
        start_timing: Optional[TimeRangeBoundary] = None,
        end_timing: Optional[TimeRangeBoundary] = None,
        active: bool = True,
    ) -> TimeSeriesRunPolicy:
        time_series_run_policy_create = TimeSeriesRunPolicyCreate(
            object="Policy",
            type="TimeSeriesRunPolicy",
            schedule_timing=to_timing_create(from_schedule_specifier(schedule_timing)),
            start_timing=to_timing_create(from_time_range_boundary(start_timing)),
            end_timing=to_timing_create(from_time_range_boundary(end_timing)),
            active=active,
        )

        time_series_run_policy = create_time_series_run_policy.request_sync(
            client=get_client(), time_series_uuid=str(self.uuid), json_body=time_series_run_policy_create
        )

        return TimeSeriesRunPolicy.parse_obj(time_series_run_policy.dict())

    def list_run_policies(self) -> List[TimeSeriesRunPolicy]:
        time_series_run_policies = list_time_series_run_policies.request_sync(
            client=get_client(), time_series_uuid=str(self.uuid)
        )

        return [
            TimeSeriesRunPolicy.parse_obj(time_series_run_policy.dict())
            for time_series_run_policy in time_series_run_policies.data
        ]
