import datetime
from dataclasses import dataclass

from sleepstudyparser.constants.BlockerType import BlockerType


@dataclass
class TopOffender:
    blocker_name: str
    blocker_type: BlockerType
    blocker_active_time_percent: int
    blocker_active_time: str

    @classmethod
    def make(cls, data):
        blocker_name = data.get("Name")
        blocker_type = data.get("Type")
        blocker_active_time_percent = data.get("ActiveTimePercent")
        # Convert from micro seconds to seconds
        blocker_active_time = data.get("ActiveTime") / 1000000
        blocker_active_time = f"{datetime.timedelta(seconds=int(blocker_active_time))}"
        return cls(
            blocker_name=blocker_name,
            blocker_type=BlockerType(blocker_type),
            blocker_active_time_percent=blocker_active_time_percent,
            blocker_active_time=blocker_active_time,
        )

    def __str__(self):
        return (
            f"\nName: {self.blocker_name:<60}"
            f"\tType: {self.blocker_type.name:<10}"
            f"\t% Active Time: {self.blocker_active_time_percent:<2}"
            f"\tActive Time: {self.blocker_active_time:<8}"
        )
