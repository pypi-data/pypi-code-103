"""Types."""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class GrandTotal:
    """GrandTotal."""

    hours: int
    minutes: int
    total_seconds: float


@dataclass
class Range:
    """Range."""

    date: str
    end: datetime
    start: datetime
    text: str
    timezone: str


@dataclass
class RangeStats:
    """Stats for one range of data."""

    grand_total: GrandTotal
    range: Range


@dataclass
class WakatimeStats:
    """Wakatime stats."""

    data: List[RangeStats]
