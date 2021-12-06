from enum import Enum
from itertools import chain


class CombinedFormat:
    def __init__(self, value):
        if isinstance(value, Enum) or isinstance(value, CombinedFormat):
            self.value = value.value
        else:
            self.value = value

    def __str__(self):
        return self.value

    def __add__(self, other):
        return CombinedFormat(CombinedFormat(self).value + CombinedFormat(other).value)

    def __sub__(self, other):
        return CombinedFormat(CombinedFormat(self).value.replace(CombinedFormat(other).value, ''))


class Format(Enum):
    NORMAL = '\x1b[0m'
    BOLD = '\x1b[1m'
    DIM = '\x1b[2m'
    UNDERLINE = '\x1b[4m'
    BLINK = '\x1b[5m'
    REVERSE = '\x1b[7m'
    STRIKE = '\x1b[9m'

    def __str__(self):
        return self.value

    def __add__(self, other):
        return CombinedFormat(self) + CombinedFormat(other)

    def __sub__(self, other):
        return CombinedFormat(self) - CombinedFormat(other)

    @staticmethod
    def remove_format(text):
        from polidoro_terminal import Color
        for f in chain(Format, Color):
            text = text.replace(f.value, '')
        return text

    @staticmethod
    def len_of_colors(text):
        from polidoro_terminal import Color
        _len = 0
        for f in chain(Format, Color):
            if f.value in text:
                _len += len(f.value)
        return _len
