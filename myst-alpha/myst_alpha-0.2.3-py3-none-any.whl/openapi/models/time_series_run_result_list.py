from typing import List

from myst.models import base_model

from ..models.time_series_run_result_get import TimeSeriesRunResultGet


class TimeSeriesRunResultList(base_model.BaseModel):
    """Schema for time series run result list responses."""

    data: List[TimeSeriesRunResultGet]
    has_more: bool
