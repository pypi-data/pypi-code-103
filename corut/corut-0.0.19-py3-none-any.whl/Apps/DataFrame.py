# -*- coding: utf-8 -*-

"""
It is aimed to provide convenience by performing many operations on the operating system.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

from ..Decorators import try_except


@try_except
def list_diff(l1, l2):
    """
    It is intended to find the difference between 2 lists or dict.
    l1 = ['a','b','c']
    l2 = ['a','b','d','c']
        result = ['d']

    l1 = {'a': 4545, 'b': 32323, 'c': 3233}
    l2 = {'a': 4545, 'b': 32323, 'c': 3233, 's': 'dd', 't': 54545}
        result = {'t', 's'}
    :param l1:
    :param l2:
    :return:
    """
    assert (
            (isinstance(l1, list) and isinstance(l2, list)) or
            (isinstance(l1, dict) and isinstance(l2, dict))
    ), 'Values must be of list or dict type.'
    s_l1 = set(l1)
    s_l2 = set(l2)
    return s_l1.union(s_l2) - s_l2.intersection(s_l1)


@try_except
def list_intersection(l1, l2):
    """
    It is aimed to find the values that intersect between the 2 lists.
    l1 = ['a','b','c']
    l2 = ['a','b','d','c']
        result = ['a', 'c', 'b']
    :param l1:
    :param l2:
    :return:
    """
    assert (isinstance(l1, list) and isinstance(l2, list)), 'Values must be of list type.'
    return list(set(l1) & set(l2))


class DataFrame:
    list_diff = staticmethod(list_diff)
    list_intersection = staticmethod(list_intersection)
