# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Created: May 10, 2018
# Modified: May 18, 2020


def intersection(set_a: list, set_b: list):
    """
    intersection of two lists with basic data type
    """
    set_c = []
    for item in set_a:
        if item in set_b:
            set_c.append(item)
    return set_c


def union(set_a: list, set_b: list):
    """
    union of two lists with basic data type
    """
    set_c = []
    set_c.extend(set_a)
    for item in set_a:
        if item in set_b:
            set_b.remove(item)
    set_c.extend(set_b)
    return set_c


def remove_sets(total_set: list, subset: list):
    """
    remove items of subset B from big set
    """
    set_c = []
    set_c.extend(total_set)
    for item in subset:
        if item in total_set:
            set_c.remove(item)
    return set_c


def split(sets: list, quantity: int):
    """
    splits a list into smaller lists, each of sub list contains 
    the (quantity) of items

    Args:
    * [sets] list to split into smaller lists
    * [quantity] the items in each sub list

    Returns:
    * [list] a new list of sub lists
    """

    output = []

    sublist = None
    max_contains = quantity

    for item in sets:

        if sublist is None:
            sublist = []

        if max_contains > 0:
            sublist.append(item)
            max_contains = max_contains - 1

        if max_contains == 0:
            output.append(sublist)
            sublist = []
            max_contains = quantity

    # something left
    if len(sublist) > 0:
        output.append(sublist)

    # finished
    return output


def clear(sets: list):
    """
    clear all element from a list
    """
    del sets
    sets = []


def cherry_pick(sets: list, item: object):
    """
    cherry pick item from sets. For example [1, 2, 3, 4, 5].
    After calling cherry_pick(sample, 3).
    The rest should be: sample = [1, 2, 4, 5]
    """
    from siki.basics import Exceptions

    if not sets or len(sets) <= 0:
        raise Exceptions.InvalidParamException("the sets is empty")

    if not isinstance(item, type(sets[0])):
        raise Exceptions.InvalidParamException("the type of element to pick from sets is invalid")

    for index in range(0, len(sets)):
        if sets[index] == item:  # element found
            return sets.pop(index)

    return None


def iterative_pick_item(sets: list):
    """
    Iteratively taking data from a given collection can be used in a for loop.
    It has the same effects as the pop function, in other words, it plays the pop in a loop
    """
    try:
        while True:
            item = sets.pop(0)
            yield item

    finally:
        return None


if __name__ == "__main__":
    my_list = [1, 2, 3, 4, 5, 6, 7, 8]
    print(cherry_pick(my_list, 5))
    print(my_list)

    my_list = ['1', '2', '3', '4', '5']
    print(cherry_pick(my_list, '3'))
    print(my_list)

    for i in iterative_pick_item(my_list):
        print(i)
