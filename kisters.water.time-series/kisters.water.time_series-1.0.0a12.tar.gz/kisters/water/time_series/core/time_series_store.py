from __future__ import annotations

import asyncio
import itertools
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generic, Iterable, List, Mapping, Optional, TypeVar, Union

import pandas as pd

from kisters.water.time_series.core.time_series import TimeSeriesColumnT, TimeSeriesT
from kisters.water.time_series.core.time_series_transaction import TimeSeriesTransaction


def make_iterable(value: Any) -> Iterable:
    """Make an infinite iterable if it's not iterable or it's string."""
    if not isinstance(value, Iterable) or isinstance(value, str):
        return itertools.repeat(value)
    return value


class TimeSeriesStore(ABC, Generic[TimeSeriesT, TimeSeriesColumnT]):
    """This abstract class defines the API of the TimeSeriesStore."""

    def get_by_path(
        self,
        *path: str,
        metadata_keys: Optional[List[str]] = None,
        **kwargs: Mapping,
    ) -> Union[TimeSeriesT, Iterable[TimeSeriesT]]:
        """
        Get the TimeSeries by path.

        Args:
            *path: The full qualified TimeSeries path.
            metadata_keys: List of metadata keys to read.  Set to None to request all metadata.
            **kwargs: The additional keyword arguments which are passed to the backend.

        Returns:
            The TimeSeries object.

        Examples:
            .. code-block:: python

                ts = store.get_by_path("W7AgentTest/20003/S/cmd")
                ts1, ts2 = store.get_by_path("example_path_1", "example_path_2")

        """
        with self.transaction() as t:
            ops = [t.read_time_series(p, metadata_keys, **kwargs) for p in path]
        time_series = (op.time_series for op in ops)
        if len(path) == 1:
            return next(time_series)
        else:
            return time_series

    def get_by_filter(
        self,
        *ts_filter: str,
        metadata_keys: Optional[List[str]] = None,
        **kwargs: Mapping,
    ) -> Iterable[TimeSeriesT]:
        """
        Get the TimeSeries list by filter.

        Args:
            *ts_filter: An iterable of TimeSeries paths or filters.
            metadata_keys: List of metadata keys to read.  Set to None to request all metadata.
            **kwargs: The additional keyword arguments, which are passed to the backend.

        Returns:
            The list of the found TimeSeries objects.

        Examples:
            .. code-block:: python

                store.get_by_filter("W7AgentTest/20004/S/*")
                store.get_by_filter("*Test", "*Ensemble")
        """
        with self.transaction() as t:
            ops = [t.filter_time_series(f, metadata_keys, **kwargs) for f in ts_filter]
        return (ts for op in ops for ts in op.time_series_iterable)

    def create_time_series(
        self, path: str, metadata: Dict = None, columns: List[TimeSeriesColumnT] = None, **kwargs
    ) -> TimeSeriesT:
        """
        Create an empty TimeSeries.

        Args:
            path: The TimeSeries path.
            metadata: The metadata of the TimeSeries.
            columns: The list of columns of the TimeSeries.
            **kwargs: Additional keyword arguments supported by the backend.
        """
        with self.transaction() as t:
            ts = t.create_time_series(path, metadata, columns, **kwargs)
        return ts.time_series

    def __getitem__(self, item: str) -> TimeSeriesT:
        return self.get_by_path(item)

    def delete_time_series(self, path: str, **kwargs) -> None:
        """
        Delete a TimeSeries.

        Args:
            path: The TimeSeries path.
            **kwargs: Additional keyword arguments supported by the backend.

        """
        with self.transaction() as t:
            t.delete_time_series(path, **kwargs)

    @abstractmethod
    def transaction(self, *, event_loop: asyncio.AbstractEventLoop = None) -> TimeSeriesTransaction:
        """
        Start a TimeSeriesTransaction.

        This is the only method to be implemented and is responsible
        of creating a TimeSeriesTransaction for the specific backend.

        Returns:
            A TimeSeriesTransaction to handle reads and writes.

        Examples:
            .. code-block:: python
                ts = store.get_by_path("test")
                with store.transaction() as t:
                    df = t.read_data_frame(ts)
                    df.loc[df.value > 27, ["quality"]] = 255
                    t.write_data_frame(df)
        """

    def read_data_frames(
        self,
        ts_list: Iterable[TimeSeriesT],
        start: Union[str, datetime, Iterable[datetime]] = None,
        end: Union[str, datetime, Iterable[datetime]] = None,
        t0: Union[datetime, Iterable[datetime]] = None,
        dispatch_info: Union[str, Iterable[str]] = None,
        member: Union[str, Iterable[str]] = None,
        **kwargs,
    ) -> Mapping[TimeSeriesT, pd.DataFrame]:
        """
        Read multiple TimeSeries as data frames.

        Args:
            ts_list: An iterable of TimeSeries.
            start: An optional iterable of datetimes representing the date from which data will be written,
                if a single datetime is passed it is used for all the TimeSeries.
            end: An optional iterable of datetimes representing the date until (included) which data will be
                written, if a single datetime is passed it is used for all the TimeSeries.
            t0: An optional iterable of datetimes used to select the t0 in an ensemble TimeSeries, if a
                single datetime is passed it is used for all the TimeSeries.
            dispatch_info: An optional iterable of str used to select the dispatch info in an ensemble
                TimeSeries, if a single str is passed it is used for all the TimeSeries.
            member: An optional iterable of str used to select the member in an ensemble TimeSeries,
                if a single str is passed it is used for all the TimeSeries.
            **kwargs: The additional keyword arguments which are passed to the backend.

        """

        futures = {}
        with self.transaction() as t:
            for ts, start_i, end_i, t0_i, dispatch_info_i, member_i in zip(
                ts_list,
                make_iterable(start),
                make_iterable(end),
                make_iterable(t0),
                make_iterable(dispatch_info),
                make_iterable(member),
            ):
                futures[ts] = t.read_data_frame(
                    ts,
                    start=start_i,
                    end=end_i,
                    t0=t0_i,
                    dispatch_info=dispatch_info_i,
                    member=member_i,
                    **kwargs,
                )
        return {k: v.data_frame for k, v in futures.items()}

    def write_data_frames(
        self,
        ts_list: Iterable[TimeSeriesT],
        data_frames: Iterable[pd.DataFrame],
        t0: Union[datetime, Iterable[datetime]] = None,
        dispatch_info: Union[str, Iterable[str]] = None,
        member: Union[str, Iterable[str]] = None,
        **kwargs,
    ):
        """
        Write multiple data frames to TimeSeries

        Args:
            ts_list: An iterable of TimeSeries
            data_frames: An iterable of DataFrames
            t0: An optional iterable of datetimes used to select the t0 in an ensemble TimeSeries,
                if a single datetime is passed it is used for all the TimeSeries.
            dispatch_info: An optional iterable of str used to select the dispatch info in an ensemble
                TimeSeries, if a single str is passed it is used for all the TimeSeries.
            member: An optional iterable of str used to select the member in an ensemble TimeSeries,
                if a single str is passed it is used for all the TimeSeries.
            **kwargs: The additional keyword arguments which are passed to the backend.

        """

        with self.transaction() as t:
            for ts_i, df_i, t0_i, dispatch_info_i, member_i in zip(
                ts_list, data_frames, make_iterable(t0), make_iterable(dispatch_info), make_iterable(member)
            ):
                t.write_data_frame(
                    time_series=ts_i,
                    data_frame=df_i,
                    t0=t0_i,
                    dispatch_info=dispatch_info_i,
                    member=member_i,
                    **kwargs,
                )


TSStoreT = TypeVar("TSStoreT", bound=TimeSeriesStore)
