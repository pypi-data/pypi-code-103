from pydantic import BaseModel
from .event import Event
from .participant_frame import ParticipantFrame
from .metadata import Metadata


class TimelineFrame(BaseModel):
    timestamp: int
    events: list[Event]
    participant_frames: dict[str, ParticipantFrame]


class TimelineInfo(BaseModel):
    frame_interval: int
    frames: list[TimelineFrame]


class Timeline(BaseModel):
    metadata: Metadata
    info: TimelineInfo
