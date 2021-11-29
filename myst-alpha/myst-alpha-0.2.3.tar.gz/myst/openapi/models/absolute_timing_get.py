from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class AbsoluteTimingGet(base_model.BaseModel):
    """Absolute timing schema for get responses."""

    time: str
    object_: Optional[Literal["Timing"]] = Field("Timing", alias="object")
    type: Optional[Literal["AbsoluteTiming"]] = "AbsoluteTiming"
