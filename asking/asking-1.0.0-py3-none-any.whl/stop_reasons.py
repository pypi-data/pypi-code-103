from enum import Enum, unique


@unique
class InternalStopReason(Enum):
    NO_MORE_ACTIONS = "NO_MORE_ACTIONS"
    NO_NEXT_STAGE = "NO_NEXT_STAGE"
