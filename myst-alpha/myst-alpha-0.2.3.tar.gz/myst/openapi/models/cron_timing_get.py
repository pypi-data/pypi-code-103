from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class CronTimingGet(base_model.BaseModel):
    """Cron timing schema for get responses."""

    cron_expression: str
    time_zone: str
    object_: Optional[Literal["Timing"]] = Field("Timing", alias="object")
    type: Optional[Literal["CronTiming"]] = "CronTiming"
