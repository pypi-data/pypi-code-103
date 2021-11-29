from typing import Optional, Union

from myst.models.timing import AbsoluteTiming, RelativeTiming, Timing
from myst.openapi.models.absolute_timing_create import AbsoluteTimingCreate
from myst.openapi.models.relative_timing_create import RelativeTimingCreate


def to_timing_create(timing: Optional[Timing]) -> Optional[Union[AbsoluteTimingCreate, RelativeTimingCreate]]:
    """Returns the appropriate OpenAPI model for the given timing, or None if timing is None."""
    if timing is None:
        return None
    elif isinstance(timing, AbsoluteTiming):
        return AbsoluteTimingCreate(object="Timing", type="AbsoluteTiming", time=timing.time.to_iso_string())
    elif isinstance(timing, RelativeTiming):
        return RelativeTimingCreate(
            object="Timing",
            type="RelativeTiming",
            frequency=timing.frequency.to_iso_string() if timing.frequency else None,
            offset=timing.offset.to_iso_string() if timing.offset else None,
            time_zone=timing.time_zone,
        )
    else:
        raise TypeError("Argument `timing` must be of type `Timing` or None.")
