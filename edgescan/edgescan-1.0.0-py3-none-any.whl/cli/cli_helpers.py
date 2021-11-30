from typing import List, Optional

import hodgepodge.click
import hodgepodge.time
import datetime


def str_to_strs(data: str) -> List[str]:
    return hodgepodge.click.str_to_strs(data)


def str_to_ints(data: str) -> List[int]:
    return hodgepodge.click.str_to_ints(data)


def str_to_datetime(data: str) -> Optional[datetime.datetime]:
    if data:
        return hodgepodge.time.to_datetime(data)
