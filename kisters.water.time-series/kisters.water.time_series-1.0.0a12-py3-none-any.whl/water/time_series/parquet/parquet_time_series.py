from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, TypeVar

from kisters.water.time_series.core.time_series import TimeSeriesColumn
from kisters.water.time_series.memory import MemoryTimeSeries


@dataclass
class ParquetTimeSeriesColumn(TimeSeriesColumn):
    PATH: ClassVar[str] = "path"
    TIMESTAMP = "ts"
    VALUE = "value"
    T0: ClassVar[str] = "t0"
    DISPATCH_INFO: ClassVar[str] = "dispatch_info"
    MEMBER: ClassVar[str] = "member"


ParquetTimeSeriesColumnT = TypeVar("ParquetTimeSeriesColumnT", bound=ParquetTimeSeriesColumn)


class ParquetTimeSeries(MemoryTimeSeries):
    """ParquetTimeSeries"""


ParquetTimeSeriesT = TypeVar("ParquetTimeSeriesT", bound=ParquetTimeSeries)
