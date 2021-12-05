# SPDX-License-Identifier: Apache-2.0

import typing as t


def cat_and(strings: t.List[str]) -> str:
    """
    >>> cat_and([])
    ''
    >>> cat_and(['a'])
    'a'
    >>> cat_and(['a', 'b'])
    'a and b'
    >>> cat_and(['a', 'b', 'c'])
    'a, b, and c'
    >>> cat_and(['a', 'b', 'c', 'd'])
    'a, b, c, and d'
    """
    if len(strings) == 0:
        return ''
    if len(strings) == 1:
        return strings[0]
    if len(strings) == 2:
        return f'{strings[0]} and {strings[1]}'
    return ', '.join(strings[:-1]) + f', and {strings[-1]}'


def cat_or(strings: t.List[str]) -> str:
    """
    >>> cat_or([])
    ''
    >>> cat_or(['a'])
    'a'
    >>> cat_or(['a', 'b'])
    'a or b'
    >>> cat_or(['a', 'b', 'c'])
    'a, b, or c'
    >>> cat_or(['a', 'b', 'c', 'd'])
    'a, b, c, or d'
    """
    if len(strings) == 0:
        return ''
    if len(strings) == 1:
        return strings[0]
    if len(strings) == 2:
        return f'{strings[0]} or {strings[1]}'
    return ', '.join(strings[:-1]) + f', or {strings[-1]}'


def first_line(s: str) -> str:
    return s[:s.find('\n')]


def partial_str(s: str, width=100) -> str:
    """
    >>> partial_str('abcd', 5)
    'abcd'

    >>> partial_str('abcde', 5)
    'abcde'

    >>> partial_str('abcdef', 5)
    'ab...'

    >>> partial_str('abcd', 2)
    Traceback (most recent call last):
        ...
    ValueError: width must be greater than 3
    """

    if width <= 3:
        raise ValueError('width must be greater than 3')

    if len(s) > width:
        s = s[:width - len('...')] + '...'
    return s
