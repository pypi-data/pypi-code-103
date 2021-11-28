from warnings import warn
from decimal import Decimal
from datetime import date, datetime
from typing import Dict, Text, Union, Optional, Mapping, List
from nasa.decorators import catch_unidentidied_error, decorate_all_methods

from nasa.warnings import InvalidInputWarning


IsoDateConvertible = Union[int, float, Decimal, Text, date, datetime]
JSONType = Optional[
    Union[Text, int, float, bool, Mapping[str, "JSONType"], List["JSONType"]]
]


@decorate_all_methods(catch_unidentidied_error)
class IsoDate:
    UNIT_CONVERSION: Dict = {
        "s": 1,
        "second": 1,
        "seconds": 1,
        "ms": 10e3,
        "millisecond": 10e3,
        "milliseconds": 10e3,
        "us": 10e6,
        "microsecond": 10e6,
        "microseconds": 10e6,
        "ns": 10e9,
        "nanosecond": 10e9,
        "nanoseconds": 10e9,
    }
    ISO_DATE_FORMAT: Text = "%Y-%m-%d"

    def __init__(
        self,
        arg: Optional[IsoDateConvertible],
        unit: Text = "s",
        format: Text = "%Y-%m-%d",
    ) -> None:
        self.dt: Optional[Union[datetime, date]]
        if arg is None:
            self.dt = None
        elif type(arg) in {int, float, Decimal}:
            if unit not in self.UNIT_CONVERSION.keys():
                message: Text = f"Invalid `unit` {unit}, will use default unit `s`. Valid unit values are {list(self.UNIT_CONVERSION.keys())}"
                warn(message, InvalidInputWarning)
            unix_seconds = arg / self.UNIT_CONVERSION.get(unit, "s")
            self.dt = datetime.utcfromtimestamp(unix_seconds)
        elif type(arg) is str:
            try:
                self.dt = datetime.strptime(arg, format)
            except ValueError:
                message: Text = (
                    f"time data {arg} does not match format {format}. Set to None"
                )
                warn(message, InvalidInputWarning)
                self.dt = None
        elif type(arg) in {date, datetime}:
            self.dt = arg
        else:
            message: Text = f"Invalid type {type(arg)} for `arg`, will set `arg` to None. Valid types for `arg` are [int, float, Decimal, str, date, datetime]"
            warn(message, InvalidInputWarning)
            self.dt = None

    def value(self) -> Optional[Text]:
        if self.dt is None:
            return None
        return self.dt.strftime(self.ISO_DATE_FORMAT)

    def __str__(self) -> Text:
        return str(self.value())

    def __repr__(self) -> Text:
        return str(self.value())
