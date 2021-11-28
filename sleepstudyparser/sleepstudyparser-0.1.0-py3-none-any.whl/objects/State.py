import datetime
from dataclasses import dataclass
from typing import Optional, List

from sleepstudyparser.constants.SessionType import SessionType
from sleepstudyparser.objects.Drips import Drips
from sleepstudyparser.objects.TopOffender import TopOffender


@dataclass
class State:
    state_type: SessionType
    start_time: datetime.datetime
    duration: datetime.timedelta
    exit_reason: str
    enter_reason: str
    drips: Optional[Drips]
    top_offenders: List[TopOffender]

    @classmethod
    def make(cls, data):
        drips = None
        state_type = SessionType(data.get("Type"))
        top_offenders = list()
        entry_time = data.get("EntryTimestampLocal")
        entry_time = entry_time.replace("Z", "+00:00")
        entry_time = datetime.datetime.fromisoformat(entry_time)
        # Convert from micro seconds to seconds
        duration_in_seconds = data.get("Duration") / 1000000
        duration = datetime.timedelta(seconds=int(duration_in_seconds))
        exit_reason = data.get("ExitReason")
        enter_reason = data.get("EnterReason")

        if state_type.value == 2:
            metadata = data.get("Metadata", dict())
            drips = Drips.make(metadata, duration_in_seconds)

        if top_blockers := data.get("TopBlockers"):
            for top_blocker in top_blockers:
                top_offenders.append(TopOffender.make(top_blocker))

        return cls(
            state_type=state_type,
            start_time=entry_time,
            duration=duration,
            exit_reason=exit_reason,
            enter_reason=enter_reason,
            drips=drips,
            top_offenders=top_offenders,
        )

    def __str__(self):
        top_offenders_str = "\n".join(
            [str(top_offender) for top_offender in self.top_offenders]
        )
        top_offenders_str = "N/A" if not top_offenders_str else top_offenders_str
        drips_str = "N/A" if self.drips is None else str(self.drips)
        return (
            f"State Type: {self.state_type.name}"
            f"\tStart Time: {self.start_time}"
            f"\tEnter Reason: {self.enter_reason}"
            f"\tExit Reason: {self.exit_reason}"
            f"\tDuration: {self.duration}"
            f"\nDrips Details: {drips_str}"
            f"\nTop Offenders: {top_offenders_str}"
        )
