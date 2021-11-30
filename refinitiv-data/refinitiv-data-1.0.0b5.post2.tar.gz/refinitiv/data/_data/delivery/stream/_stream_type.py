from enum import auto, unique, Enum


@unique
class StreamType(Enum):
    OMM = auto()
    RDP = auto()
