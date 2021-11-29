from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class RelativeTimingGet(base_model.BaseModel):
    """Relative timing schema for get responses."""

    time_zone: str
    object_: Optional[Literal["Timing"]] = Field("Timing", alias="object")
    type: Optional[Literal["RelativeTiming"]] = "RelativeTiming"
    frequency: Optional[str] = None
    offset: Optional[str] = None
