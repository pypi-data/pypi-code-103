from __future__ import annotations

import asyncio
from typing import TypeVar

from kisters.water.time_series.core.time_series import TimeSeriesColumnT
from kisters.water.time_series.core.time_series_store import TimeSeriesStore
from kisters.water.time_series.memory.memory_time_series import MemoryTimeSeriesT
from kisters.water.time_series.memory.memory_time_series_transaction import MemoryTimeSeriesTransaction


class MemoryStore(TimeSeriesStore[MemoryTimeSeriesT, TimeSeriesColumnT]):
    """FileStore provides a TimeSeriesStore for in memory data

    Args:

    Examples:
        .. code-block:: python

            from kisters.water.time_series.file_io import MemoryStore
            fs = MemoryStore()
            ts = fs.get_by_path('validation/inner_consistency1/station1/H')
    """

    def __init__(self):
        self._time_series = {}

    def transaction(self, *, event_loop: asyncio.AbstractEventLoop = None) -> MemoryTimeSeriesTransaction:
        return MemoryTimeSeriesTransaction(self, event_loop=event_loop)


MemoryStoreT = TypeVar("MemoryStoreT", bound=MemoryStore)
