from enum import Enum, unique


@unique
class Range(Enum):
    NONE = 0
    START = 1
    END = 2
