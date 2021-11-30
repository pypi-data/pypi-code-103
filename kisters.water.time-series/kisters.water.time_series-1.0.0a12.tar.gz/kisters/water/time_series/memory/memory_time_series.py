from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypeVar

import pandas as pd

from kisters.water.time_series.core import TimeSeries, TimeSeriesMetadata
from kisters.water.time_series.core.time_series import EnsembleMemberInfo, TimeSeriesColumnT

if TYPE_CHECKING:
    from kisters.water.time_series.memory.memory_store import MemoryStoreT
else:
    MemoryStoreT = TypeVar("MemoryStoreT")


class MemoryTimeSeries(TimeSeries[MemoryStoreT, TimeSeriesColumnT]):
    def __init__(
        self,
        store: MemoryStoreT,
        path: str,
        metadata: Dict[str, Any],
        data: Dict[EnsembleMemberInfo, pd.DataFrame],
    ):
        """
        Create a TimeSeries object directly with the metadata and data given.

        Args:
            store: Parent TimeSeriesStore object.
            path: Time series path.
            metadata: Mapping with all the metadata of the TimeSeries.
            data: Dict of DataFrame objects containing TimeSeries data.
        """
        super().__init__(store)
        self._path = path
        self._metadata = TimeSeriesMetadata(self, metadata)
        self._data = data

    @property
    def path(self) -> str:
        return self._path

    @property
    def metadata(self) -> TimeSeriesMetadata:
        return self._metadata

    def coverage_from(
        self,
        t0: Optional[datetime] = None,
        dispatch_info: Optional[str] = None,
        member: Optional[str] = None,
        **kwargs
    ) -> datetime:
        return self._data[EnsembleMemberInfo(t0, dispatch_info, member)].index[0]

    def coverage_until(
        self,
        t0: Optional[datetime] = None,
        dispatch_info: Optional[str] = None,
        member: Optional[str] = None,
        **kwargs
    ) -> datetime:
        return self._data[EnsembleMemberInfo(t0, dispatch_info, member)].index[-1]

    def coverage(
        self,
        t0: Optional[datetime] = None,
        dispatch_info: Optional[str] = None,
        member: Optional[str] = None,
        **kwargs
    ) -> Dict[str, datetime]:
        return {
            "min": self.coverage_from(t0, dispatch_info, member),
            "max": self.coverage_until(t0, dispatch_info, member),
        }

    def ensemble_members(
        self, t0_start: Optional[datetime] = None, t0_end: Optional[datetime] = None, **kwargs
    ) -> List[EnsembleMemberInfo]:
        return list(self._data.keys())


MemoryTimeSeriesT = TypeVar("MemoryTimeSeriesT")
