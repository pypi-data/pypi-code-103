from enum import Enum, unique


@unique
class Host(Enum):
    SHELL = 0
    TERMINAL = 1
