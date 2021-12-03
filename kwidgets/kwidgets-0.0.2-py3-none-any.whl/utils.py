""" Various generic utility functions.

Adapted from: https://www.geeksforgeeks.org/python-merge-two-lists-alternatively/
"""
from typing import List, Iterable, Union


def intersperse(iteratorables: List[Iterable]):
    """ Given a list of iterables, return a single list with all the individual items interspersed

    For example: [[1,2,3], [4,5,6]] should return [1,4,2,5,3,6].

    :param iteratorables:
    :return:
    """
    iters = [iter(i) for i in iteratorables]
    while True:
        for i in iters:
            try:
                yield i.__next__()
            except StopIteration:
                return


def to_xy(values: List[Union[int, float]]):
    """  Split a list of points into an x,y sequence

    :param values:  A list of values in the form [x1,y1,x2,y2,...]
    :return:  Two lists, one for X and one for y
    """
    return [values[i] for i in range(0,len(values), 2)], [values[i] for i in range(1,len(values), 2)]
