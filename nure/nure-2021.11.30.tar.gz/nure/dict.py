import collections.abc


def update(default, modified):
    for k, v in modified.items():
        if isinstance(v, collections.abc.Mapping):
            default[k] = update(default.get(k, {}), v)
        else:
            default[k] = v
    return default
