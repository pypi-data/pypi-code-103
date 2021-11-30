from __future__ import annotations

from kisters.water.time_series.core.time_series import TimeSeries, TimeSeriesMetadata


class TimeSeriesDecorator(TimeSeries):
    def __init__(self, forward: TimeSeries):
        super().__init__(forward.store, forward.columns)
        self._forward = forward

    @property
    def path(self) -> str:
        return self._forward.path

    @property
    def metadata(self) -> TimeSeriesMetadata:
        return self._forward.metadata
