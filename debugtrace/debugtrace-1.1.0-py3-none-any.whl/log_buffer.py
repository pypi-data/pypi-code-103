# log_buffer.py
# (C) 2020 Masato Kokubo
from __future__ import annotations
import sys

class LogBuffer(object):
    '''
    Buffers logs.
    '''
    __slots__ = [
        '_maximum_data_output_width',
        '_nest_level',
        '_append_nest_level',
        '_lines',
        '_last_line'
    ]

    def __init__(self, maximum_data_output_width: int) -> None:
        '''
        Initializes this object.
        '''
        self._maximum_data_output_width = maximum_data_output_width
        self._nest_level = 0
        self._append_nest_level = 0

        # tuples of data indentation level and log string
        self._lines = []

        # buffer for a line of logs
        self._last_line = ''

    def line_feed(self) -> None:
        '''
        Breaks the current line.
        '''
        self._lines.append((self._nest_level + self._append_nest_level, self._last_line.rstrip()))
        self._append_nest_level = 0
        self._last_line = ""

    def up_nest(self) -> None:
        '''
        Ups the data nest level.
        '''
        self._nest_level += 1

    def down_nest(self) -> None:
        '''
        Downs the data nest level.
        '''
        self._nest_level -= 1

    def append(self, value: object, nest_level:int = 0, no_break: bool = False) -> __class__:
        '''
        Appends a string representation of the value.

        Args:
            value (object): The value to append
            nest_level (int, optional): The nest level of the value. Defaults to 0
            no_break (bool, optional): If true, does not break even if the maximum width is exceeded.
                Defaults to False

        Returns:
            LogBuffer: This object
        '''
        if value is not None:
            string = str(value)
            if not no_break and self.length > 0 and self.length + len(string) > self._maximum_data_output_width:
                self.line_feed()
            self._append_nest_level = nest_level
            self._last_line += string
        return self

    def no_break_append(self, value: object) -> __class__:
        '''
        Appends a string representation of the value.
        Does not break even if the maximum width is exceeded.

        Args:
            value (object): The value to append

        Returns:
            LogBuffer: This object
        '''
        return self.append(value, 0, True)

    def append_buffer(self, separator: str, buff: __class__) -> __class__:
        '''
        Appends lines of another LogBuffer.

        Args:
            separator (str): The separator string to append if not None
            buff (LogBuffer): Another LogBuffer

        Returns:
            LogBuffer: This object
        '''
        if separator is not None:
            self.append(separator, 0, True)
        index = 0
        for line in buff.lines:
            if index > 0:
                self.line_feed()
            self.append(line[1], line[0], index == 0 and separator is not None)
            index += 1
        return self

    @property
    def length(self) -> int:
        '''
        The length of the last line.
        '''
        return len(self._last_line)

    @property
    def is_multi_lines(self) -> bool:
        '''
        True if multiple line, false otherwise.
        '''
        return len(self._lines) > 1 or len(self._lines) == 1 and self.length > 0

    @property
    def lines(self) -> list:
        '''
        A list of tuple of data indentation level and log string.
        '''
        lines = self._lines.copy()
        if self.length > 0:
            lines.append((self._nest_level, self._last_line))
        return lines
