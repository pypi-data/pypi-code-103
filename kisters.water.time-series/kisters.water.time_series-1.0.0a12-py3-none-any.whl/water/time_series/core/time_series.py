from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Generic, Iterator, List, Mapping, Optional, TypeVar, Union

import numpy as np
import pandas as pd

from kisters.water.time_series.core.time_series_metadata import TimeSeriesMetadata

if TYPE_CHECKING:
    from kisters.water.time_series.core.time_series_store import TSStoreT
else:
    TSStoreT = TypeVar("TSStoreT")


@dataclass(frozen=True)
class EnsembleMemberInfo(Mapping):
    """
    Helper dataclass for retrieving Ensemble members information.

    Implements Mapping to make it easy to use together with read_data_frame/write_data_frame methods.
    This class is immutable, so that it can be used in MemoryStore as dict keys safely.

    Examples:
        .. code-block:: python

            ensemble_infos = ts.read_ensemble_members(t0=datetime(2020,1,1))
            df = ts.read_data_frame(**ensemble_infos[0])

    """

    t0: datetime
    dispatch_info: Optional[str]
    member: Optional[str]

    def __init__(self, t0: datetime, dispatch_info: Optional[str] = None, member: Optional[str] = None):
        super().__setattr__("t0", t0)
        super().__setattr__(
            "dispatch_info", dispatch_info if not self.is_null_like(dispatch_info) else None
        )
        super().__setattr__("member", member if not self.is_null_like(member) else None)

    def __getitem__(self, key: str) -> Union[str, datetime]:
        return self.__dict__[key]

    def __len__(self) -> int:
        return self.__dict__.__len__()

    def __iter__(self) -> Iterator[str]:
        return self.__dict__.__iter__()

    @staticmethod
    def is_null_like(s: str):
        return s in {"", "-"} or s is None


@dataclass
class TimeSeriesColumn:
    """
    Dataclass to hold TimeSeries columns information.
    """

    key: str
    dtype: np.dtype


TimeSeriesColumnT = TypeVar("TimeSeriesColumnT", bound=TimeSeriesColumn)


class TimeSeries(ABC, Generic[TSStoreT, TimeSeriesColumnT]):
    """This class provides the interface of TimeSeries."""

    def __init__(self, store: TSStoreT, columns: Optional[List[TimeSeriesColumnT]] = None):
        self._store = store
        self._columns = columns if columns is not None else []

    def __str__(self) -> str:
        """Return the string representations for the TimeSeries."""
        return self.path

    def __repr__(self, *args, **kwargs) -> str:
        return f"{self.__class__.__name__} {self.path}"

    @property
    @abstractmethod
    def path(self) -> str:
        """
        The full path to this TimeSeries.

        Returns:
             The path string.
        """

    @property
    def store(self) -> TSStoreT:
        """
        The TimeSeriesStore in charge of retrieving this TimeSeries from the backend.

        Returns:
             The TimeSeriesStore.
        """
        return self._store

    @property
    def columns(self) -> List[TimeSeriesColumnT]:
        """
        The columns of the TimeSeries.

        Returns:
            A list of TimeSeriesColumn.
        """
        return self._columns

    @property
    @abstractmethod
    def metadata(self) -> TimeSeriesMetadata:
        """
        The metadata dictionary.

        Notes:
            Changes made to this object are not reflected in the backend until
            an explicit call to :func:`~kisters.water.time_series.core.TimeSeries.write_metadata`

        Returns:
            A dict object holding the TimeSeries metadata.
        """

    def coverage_from(
        self,
        t0: Optional[datetime] = None,
        dispatch_info: Optional[str] = None,
        member: Optional[str] = None,
        **kwargs,
    ) -> datetime:
        """
        Get the coverage from which the TimeSeries data starts.

        Args:
            Only needed for ensemble TimeSeries.
            t0: The t0 time stamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier.

        Returns:
            The datetime.
        """
        return self.coverage(t0=t0, dispatch_info=dispatch_info, member=member, **kwargs)["min"]

    def coverage_until(
        self,
        t0: Optional[datetime] = None,
        dispatch_info: Optional[str] = None,
        member: Optional[str] = None,
        **kwargs,
    ) -> datetime:
        """
        Get the coverage until which the TimeSeries data covers.

        Args:
            Only needed for ensemble TimeSeries.
            t0: The t0 time stamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier.

        Returns:
            The datetime.
        """
        return self.coverage(t0=t0, dispatch_info=dispatch_info, member=member, **kwargs)["max"]

    def coverage(
        self,
        t0: Optional[datetime] = None,
        dispatch_info: Optional[str] = None,
        member: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, datetime]:
        """
        Get the coverage until which the TimeSeries data covers.

        Args:
            Only needed for ensemble TimeSeries.
            t0: The t0 time stamp of the ensemble member.
            dispatch_info: Ensemble dispatch_info identifier.
            member: Ensemble member identifier.

        Returns:
            The datetime.
        """
        with self.store.transaction() as t:
            op = t.get_coverage(self, t0=t0, dispatch_info=dispatch_info, member=member, **kwargs)
        return op.coverage

    def ensemble_members(
        self, t0_start: Optional[datetime] = None, t0_end: Optional[datetime] = None, **kwargs
    ) -> List[EnsembleMemberInfo]:
        """
        Returns a list of dictionaries with the corresponding t0, member and dispatch_infos as key.

        Args:
            t0_start: The starting date from which the data will be returned.
            t0_end: The ending date until which the data will be covered (end date included).

        Returns:
            A dictionary with the ensemble members information
        """
        with self.store.transaction() as t:
            op = t.get_ensemble_members(self, t0_start=t0_start, t0_end=t0_end, **kwargs)
        return op.ensemble_members

    def read_data_frame(
        self,
        start: Optional[Union[str, datetime]] = None,
        end: Optional[Union[str, datetime]] = None,
        t0: Optional[datetime] = None,
        dispatch_info: Optional[str] = None,
        member: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        This method returns the TimeSeries data between the start and end dates (both dates included)
        structured as a pandas DataFrame.

        Args:
            start: The starting date from which the data will be returned, expressed either
                as an ISO Datetime string or as a datetime object. If TimeZone is not included,
                it assumes the TimeZone of the TimeSeries.
            end: The ending date until which the data will be covered (end date included),
                expressed either as an ISO Datetime string or as a datetime object. If TimeZone
                is not included, it assumes the TimeZone of the TimeSeries.

            For ensemble time series only:
                To retrieve all data points of all dispatch_infos and members set t0, dispatch_info, member
                to None including t0, dispatch_info, member as additional columns

                To retrieve a single ensemble member:
                    t0: The t0 time stamp of the ensemble member.
                    dispatch_info: Ensemble dispatch_info identifier.
                    member: Ensemble member identifier.

        Returns:
            The DataFrame containing the TimeSeries data
        """
        with self.store.transaction() as t:
            read = t.read_data_frame(
                self, start=start, end=end, t0=t0, dispatch_info=dispatch_info, member=member, **kwargs
            )
        return read.data_frame

    def write_data_frame(
        self,
        data_frame: pd.DataFrame,
        t0: Optional[datetime] = None,
        dispatch_info: Optional[str] = None,
        member: Optional[str] = None,
        **kwargs,
    ):
        """
        This methods writes the TimeSeries data from the data_frame into this TimeSeries.

        Args:
            data_frame: The TimeSeries data to be written in the form of a pandas DataFrame.

            For ensemble time series only:
                To write a single ensemble member at once
                    t0: The t0 time stamp of the ensemble member.
                    dispatch_info: Ensemble dispatch_info identifier.
                    member: Ensemble member identifier
        """
        with self.store.transaction() as t:
            t.write_data_frame(
                self, data_frame, t0=t0, dispatch_info=dispatch_info, member=member, **kwargs
            )

    def delete_data_range(
        self,
        start: Optional[Union[str, datetime]] = None,
        end: Optional[Union[str, datetime]] = None,
        t0: Optional[datetime] = None,
        dispatch_info: Optional[str] = None,
        member: Optional[str] = None,
        **kwargs,
    ):
        """
        This methods deletes a range of data and/or an ensemble member from a time series.

        Args:
            start: The starting date from which the data will be returned, expressed either
                as an ISO Datetime string or as a datetime object. If TimeZone is not included,
                it assumes the TimeZone of the TimeSeries.
            end: The ending date until which the data will be covered (end date included),
                expressed either as an ISO Datetime string or as a datetime object. If TimeZone
                is not included, it assumes the TimeZone of the TimeSeries.

            For ensemble time series only:
                To write a single ensemble member at once
                    t0: The t0 time stamp of the ensemble member.
                    dispatch_info: Ensemble dispatch_info identifier.
                    member: Ensemble member identifier
        """
        with self.store.transaction() as t:
            t.delete_data_range(
                self, start=start, end=end, t0=t0, dispatch_info=dispatch_info, member=member, **kwargs
            )


TimeSeriesT = TypeVar("TimeSeriesT", bound=TimeSeries)
