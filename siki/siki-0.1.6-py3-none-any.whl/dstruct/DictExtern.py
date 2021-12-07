# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Created: May 10, 2018
# Modified: May 18, 2020

from siki.basics import Exceptions


def intersection(set_a: dict, set_b):
    """
    intersection of two dictionaries with basic data type
    """
    set_c = {}

    for _key, _value in set_a.items():
        if _key in set_b and set_b[_key] == _value:
            set_c[_key] = _value

    return set_c


def union(set_a: dict, set_b: dict):
    """
    union of two dictionaries with basic data type
    """
    set_c = {}

    for _key, _value in set_a.items():
        set_c[_key] = _value

    for _key, _value in set_b.items():
        set_c[_key] = _value

    return set_c


def remove_sets(total_set, subset):
    """
    remove sub set from big set
    """
    backup = total_set.copy()
    set_c = intersection(total_set, subset)

    for key in set_c.keys():
        backup.pop(key)

    set_c.clear()

    return backup


def find_out_subset(total_set, sub_key_list):
    """
    find out sub dictionary of a dictionary with given list of keys.
    """
    output = {}

    for key in sub_key_list:
        if key in total_set.keys():
            output[key] = total_set[key]

    return output


def create_dict_by_list(key_list, default=None):
    """
    given a list, and extend the list to a dictionary type, with all values are set to None (default)
    """
    output = {}

    if type(default) is dict:
        raise Exceptions.InvalidParamException("dict type cannot be set to a new dict value")

    if type(default) is list:
        if len(default) != len(key_list):
            raise Exceptions.InvalidParamException("default as a list have different length to key list")
        else:
            for i in range(0, len(key_list)):
                output[key_list[i]] = default[i]

            # return from two list
            return output

    # else, normal cases
    for key in key_list:
        output[key] = default

    # success
    return output


def clear(sets):
    """
    clear all element from a list
    """
    del sets
    sets = {}


def have_same_keys(set_a: dict, set_b: dict):
    """
    test set a and set b have the same keys
    """
    keys_from_a = set_a.keys()
    keys_from_b = set_b.keys()

    if len(keys_from_a) != len(keys_from_b):  # length different
        return False

    for key, _ in set_a.items():
        if key not in set_b.keys():  # key not in another dictionary
            return False

    return True


def have_same_vals(set_a: dict, set_b: dict):
    """
    test set a and set b have the same values
    """
    vals_from_a = set_a.values()
    vals_from_b = set_b.values()

    if len(vals_from_a) != len(vals_from_b):  # length different
        return False

    for _, val in set_a.items():
        if val not in set_b.values():  # val not in another dictionary
            return False

    return True


def have_same_items(set_a: dict, set_b: dict):
    """
    test set a and set b have the same items
    """
    keys_from_a = set_a.keys()
    keys_from_b = set_b.keys()

    if len(keys_from_a) != len(keys_from_b):  # length different
        return False

    for key, val in set_a.items():
        if key not in set_b.keys():  # key not in another dictionary
            return False

        if val != set_b[key]:
            return False

    return True


def iterative_pick_item(sets: dict):
    """
    Iteratively taking data from a given collection can be used in a for loop.
    It has the same effects as the pop function, in other words, it plays the pop in a loop
    """
    try:
        while True:
            item = sets.popitem()
            yield item

    finally:
        return None


if __name__ == "__main__":
    dict_a = {'a': 1, 'b': 2, 'c': 3}
    dict_b = {'a': 1, 'b': 2, 'c': 4}
    dict_c = {'d': 1, 'b': 2, 'c': 4}
    dict_d = {'a': 1, 'b': 2, 'c': 3}

    print(have_same_keys(dict_a, dict_b))
    print(have_same_vals(dict_a, dict_b))
    print(have_same_keys(dict_c, dict_a))

    print(have_same_items(dict_a, dict_d))
    print(have_same_items(dict_a, dict_b))

    for i in iterative_pick_item(dict_a):
        print(i)