from typing import Optional, Union, List
from dataclasses import dataclass
from edgescan.data.types.object import Object

import hodgepodge.time
import datetime


@dataclass(frozen=True)
class License(Object):
    id: int
    name: str
    license_type_id: int
    license_type_name: str
    asset_id: Optional[int]
    order_id: int
    start_date: datetime.datetime
    end_date: datetime.datetime
    expired: bool
    status: Optional[str]

    def is_expired(self) -> bool:
        return self.expired

    def matches(
            self,
            ids: Optional[List[int]] = None,
            names: Optional[List[str]] = None,
            min_start_date: Optional[Union[str, int, float, datetime.datetime, datetime.date]] = None,
            max_start_date: Optional[Union[str, int, float, datetime.datetime, datetime.date]] = None,
            min_end_date: Optional[Union[str, int, float, datetime.datetime, datetime.date]] = None,
            max_end_date: Optional[Union[str, int, float, datetime.datetime, datetime.date]] = None,
            expired: Optional[bool] = None) -> bool:

        #: Filter licenses by ID.
        if ids and self.id not in ids:
            return False

        #: Filter licenses by name.
        if names and self.name not in names:
            return False

        #: Filter licenses based on whether or not they are expired.
        if expired is not None and expired != self.expired:
            return False

        #: Filter licenses by [min|max] [start|end] time.
        for timestamp, min_timestamp, max_timestamp in (
            (self.start_date, min_start_date, max_start_date),
            (self.end_date, min_end_date, max_end_date),
        ):
            if (min_timestamp or max_timestamp) and \
                    not hodgepodge.time.in_range(timestamp, minimum=min_timestamp, maximum=max_timestamp):
                continue

        return True

    def __hash__(self):
        return self.id
