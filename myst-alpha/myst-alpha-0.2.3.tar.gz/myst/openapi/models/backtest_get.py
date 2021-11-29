from typing import Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model

from ..models.absolute_timing_get import AbsoluteTimingGet
from ..models.cron_timing_get import CronTimingGet
from ..models.relative_timing_get import RelativeTimingGet


class BacktestGet(base_model.BaseModel):
    """Schema for backtest get responses."""

    uuid: str
    create_time: str
    title: str
    description: str
    test_start_time: str
    test_end_time: str
    fit_start_timing: Union[AbsoluteTimingGet, RelativeTimingGet]
    fit_end_timing: Union[AbsoluteTimingGet, RelativeTimingGet]
    fit_reference_timing: Union[AbsoluteTimingGet, CronTimingGet]
    predict_start_timing: RelativeTimingGet
    predict_end_timing: RelativeTimingGet
    predict_reference_timing: CronTimingGet
    project: str
    model: str
    creator: str
    object_: Optional[Literal["Backtest"]] = Field("Backtest", alias="object")
    update_time: Optional[str] = None
