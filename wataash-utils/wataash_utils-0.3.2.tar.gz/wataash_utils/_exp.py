# SPDX-License-Identifier: Apache-2.0

"""
Experimental, unstable
"""

import dataclasses
import re

import wcwidth

import wataash_utils as wu


# -----------------------------------------------------------------------------
# str

def wc_slice(s: str, wc_start: int, wc_stop: int) -> str:
    """
    >>> '世界'[0:1]
    '世'

    >>> wc_slice('世界', 0, 2)
    '世'

    >>> wc_slice('世界', 2, 4)
    '界'

    >>> wc_slice('世界', 0, 4)
    '世界'

    >>> wc_slice('世界', 0, 1)
    Traceback (most recent call last):
        ...
    IndexError: wc_stop:1 is within a character

    >>> wc_slice('世界', 1, 4)
    Traceback (most recent call last):
        ...
    IndexError: wc_start:1 is within a character

    >>> wc_slice('世界', 0, 6)
    Traceback (most recent call last):
        ...
    IndexError: wc_stop:6 is out of range

    >>> wc_slice('世界', 6, 8)
    Traceback (most recent call last):
        ...
    IndexError: wc_start:6 is out of range

    >>> wc_slice('世界', 4, 0)
    Traceback (most recent call last):
        ...
    ValueError: wc_stop(0) <= wc_start(4)
    """

    if wc_stop <= wc_start:
        raise ValueError(f'wc_stop({wc_stop}) <= wc_start({wc_start})')

    wc_width = wc_stop - wc_start
    wc_discard = wc_start

    ret = ''
    for c in s:
        w = wcwidth.wcwidth(c)
        if wc_discard == 0:
            wc_width -= w
            if wc_width < 0:
                # XXX: https://docs.python.org/3/library/exceptions.html
                #   > exception IndexError
                #   > Raised when a sequence subscript is out of range.
                #   ...this is not out of range!
                raise IndexError(f'wc_stop:{wc_stop} is within a character')
            ret += c
            if wc_width == 0:
                return ret
        else:
            wc_discard -= w
            if wc_discard < 0:
                raise IndexError(f'wc_start:{wc_start} is within a character')
    if wc_discard == 0:
        raise IndexError(f'wc_stop:{wc_stop} is out of range')
    else:
        raise IndexError(f'wc_start:{wc_start} is out of range')


@dataclasses.dataclass(frozen=True)
class Column:
    wc_start: int
    wc_stop: int
    name: str

    def __repr__(self):
        return f'({self.wc_start}-{self.wc_stop} {repr(self.name)})'


def _parse_header(header: str) -> list[Column]:
    """
    # >>> #             0-4 4-8 8-11
    # >>> #             ┌  ┐┌  ┐┌ ┐
    # >>> _parse_header('a   bb  ccc')
    # [(0-4 'a'), (4-8 'bb'), (8-11 'ccc')]
    #
    # >>> #             0-6   6-10 10-13
    # >>> #             ┌    ┐┌  ┐┌ ┐
    # >>> _parse_header('  a   bb  ccc')
    # [(0-6 'a'), (6-10 'bb'), (10-13 'ccc')]

    >>> #             0-4  4-9
    >>> #             ┌   ┐┌   ┐
    >>> _parse_header(' あ 世界 ')
    [(0-4 'あ'), (4-9 '世界')]

    >>> _parse_header(' ')
    []
    """
    columns = []
    header = header + ' '  # ensure ends with \s+
    wc_pos = 0
    for match in re.finditer(r'\s*(\S+)\s+', header):
        wc_width = wcwidth.wcswidth(match[0])
        assert match.start() <= wc_pos  # <: when header[:match.start()] includes full-width
        assert match.end() - match.start() <= wc_width  # <: when match[1] includes full-width
        assert wc_slice(header, wc_pos, wc_pos + wc_width) == match[0]
        # columns.append(Column(slice(match.start(), match.end()), match[1]))
        columns.append(Column(wc_pos, wc_pos + wc_width, match[1]))
        wc_pos += wc_width
    if not columns:
        return []
    assert wcwidth.wcswidth(header) == columns[-1].wc_stop
    columns[-1] = Column(columns[-1].wc_start, columns[-1].wc_stop - 1, columns[-1].name)
    return columns


def parse_fixed_width_table(table: str) -> list[dict[str, str]]:
    """
    # TODO: doctest BUG! parsing '\' is incorrect
    >>> table = '''\
    ... hello         世界   world
    ...               1          2
    ...        3           abcdefghi
    ... foo
    ... '''
    >>> print(table[:6])
        ..

    >>> table = '''
    ... hello         世界   world
    ...               1          2
    ...        3           abcdefghi
    ... foo
    ... '''
    >>> print(table)
    <BLANKLINE>
    hello         世界   world
                  1          2
    3                    12345678
    foo
    <BLANKLINE>
    >>> parse_fixed_width_table(table[1:])
    [{'hello': '', '世界': '1', 'world': '2'}, {'hello': '3', '世界': 'ab', 'world': 'cdefghi'}, {'hello': 'foo', '世界': '', 'world': ''}]

    :param table:
    :return:
    """

    columns = _parse_header(wu.str.first_line(table))

    dicts = []

    for line in table.rstrip('\n').split('\n')[1:]:
        wc_line_width = wcwidth.wcswidth(line)
        line_dic = {}
        for column in columns:
            try:
                line_dic[column.name] = wc_slice(line, column.wc_start, column.wc_stop).strip()
                assert column.wc_stop <= wc_line_width
            except IndexError as e:
                assert wc_line_width < column.wc_stop
                if e.args[0] == f'wc_start:{column.wc_start} is out of range':
                    assert wc_line_width < column.wc_start
                    line_dic[column.name] = ''
                elif e.args[0] == f'wc_stop:{column.wc_stop} is out of range':
                    line_dic[column.name] = wc_slice(line, column.wc_start, wc_line_width).strip()
                else:
                    raise Exception('BUG')
        dicts.append(line_dic)
    return dicts
