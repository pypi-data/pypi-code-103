from enum import Enum

from polidoro_terminal.format import CombinedFormat


class Color(Enum):
    BLACK = "\x1b[30m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    MAGENTA = "\x1b[35m"
    CYAN = "\x1b[36m"
    WHITE = "\x1b[37m"

    LIGHT_BLACK = "\x1b[90m"
    LIGHT_RED = "\x1b[91m"
    LIGHT_GREEN = "\x1b[92m"
    LIGHT_YELLOW = "\x1b[93m"
    LIGHT_BLUE = "\x1b[94m"
    LIGHT_MAGENTA = "\x1b[95m"
    LIGHT_CYAN = "\x1b[96m"
    LIGHT_WHITE = "\x1b[97m"

    BACKGROUND_BLACK = "\x1b[40m"
    BACKGROUND_RED = "\x1b[41m"
    BACKGROUND_GREEN = "\x1b[42m"
    BACKGROUND_YELLOW = "\x1b[43m"
    BACKGROUND_BLUE = "\x1b[44m"
    BACKGROUND_MAGENTA = "\x1b[45m"
    BACKGROUND_CYAN = "\x1b[46m"
    BACKGROUND_WHITE = "\x1b[47m"

    BACKGROUND_LIGHT_BLACK = "\x1b[100m"
    BACKGROUND_LIGHT_RED = "\x1b[101m"
    BACKGROUND_LIGHT_GREEN = "\x1b[102m"
    BACKGROUND_LIGHT_YELLOW = "\x1b[103m"
    BACKGROUND_LIGHT_BLUE = "\x1b[104m"
    BACKGROUND_LIGHT_MAGENTA = "\x1b[105m"
    BACKGROUND_LIGHT_CYAN = "\x1b[106m"
    BACKGROUND_LIGHT_WHITE = "\x1b[107m"

    def __str__(self):
        return self.value

    def __add__(self, other):
        return CombinedFormat(self) + CombinedFormat(other)

    def __sub__(self, other):
        return CombinedFormat(self) - CombinedFormat(other)
