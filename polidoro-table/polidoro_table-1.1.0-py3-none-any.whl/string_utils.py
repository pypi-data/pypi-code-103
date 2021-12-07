from enum import Enum


class Align(Enum):
    LEFT = '<'
    RIGHT = '>'
    CENTER = '^'


def fill(text, size, align=None, char=' '):
    from polidoro_table import Format
    size += Format.len_of_colors(text)
    align = align or Align.LEFT
    return '{0:{char}{align}{size}}'.format(text, char=char, align=align.value, size=size)
