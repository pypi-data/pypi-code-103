from collections import Mapping, OrderedDict


def merged_non_empty(d1: dict, d2: dict) -> dict:
    return {
        k: (d1.get(k) or d2.get(k))
        for k in set(d1) | set(d2)
    }


def insert_at_pos_ordered_dict(dic,
                               current_key_dict=None,
                               item=None,
                               key_to_insert_after=None):
    if item is None:
        return
    d = OrderedDict()
    insert_at_first = key_to_insert_after is None
    if insert_at_first:
        d[current_key_dict] = item
    for dic_k, dic_v in dic.items():
        d[dic_k] = dic_v
        if not insert_at_first and dic_k == key_to_insert_after:
            d[current_key_dict] = item
    # Replace with new ordered
    dic.clear()
    dic.update(d)


def ordered_dict_merge(result_d: OrderedDict,
                       complement_d: OrderedDict):
    """ Recursive OrderedDict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, ordered_dict_merge recurse down into dicts nested
    to an arbitrary depth, updating keys. The ``complement_d`` is merged into
    ``result_d``.

    :param result_d: dict onto which the merge is executed
    :param complement_d: dct merged into dct
    :return: None
    """
    for k, v in complement_d.items():
        if k in result_d and isinstance(result_d[k], OrderedDict) \
                and isinstance(v, OrderedDict):
            ordered_dict_merge(result_d[k], v)
        else:
            result_d[k] = v


def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurse down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.iteritems():
        if k in dct and isinstance(dct[k], dict) \
                and isinstance(merge_dct[k], Mapping):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
