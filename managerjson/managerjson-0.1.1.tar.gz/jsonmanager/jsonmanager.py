from itertools import chain, starmap
import keyword
from collections import abc


class JsonObject:
    key_words = ["json"]

    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)
        elif isinstance(arg, abc.Mapping):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, mapping):
        self.__data = {}
        for key, value in mapping.items():
            key = key.replace(":", "")
            if keyword.iskeyword(key) or key in self.key_words:
                key += "_"
            self.__data[key] = value

    @property
    def json(self):
        return self.__data

    def __contains__(self, key):
        return key in self.__data

    def __getattr__(self, name):
        return self._get_attr(name)

    def __getitem__(self, key):
        return self._get_attr(key)

    def _get_attr(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            try:
                return JsonObject(self.__data[name])
            except KeyError:
                raise AttributeError

    def __str__(self):
        return f"{list(self.__data.keys())}"

    def __repr__(self):
        return f"{list(self.__data.items())}"


def flatjson(to_flat):

    while True:
        to_flat = dict(chain.from_iterable(starmap(_unpack, to_flat.items())))
        if _atomic_values(to_flat):
            break
    return to_flat


def _atomic_values(to_flat):
    return not _nested_dict(to_flat) and not _nested_list(to_flat)


def _process_dict_values(parent_key, key, value):
    temp1 = parent_key + "_" + key
    return temp1, value


def _proccess_list(parent_key, i, value):
    temp2 = parent_key + "_" + str(i)
    return temp2, value


def _nested_dict(to_flat):
    return any(isinstance(value, dict) for value in to_flat.values())


def _nested_list(to_flat):
    return any(isinstance(value, list) for value in to_flat.values())


def _unpack(parent_key, parent_value):

    if isinstance(parent_value, dict):
        for key, value in parent_value.items():
            key = key.replace(":", "")
            yield _process_dict_values(parent_key, key, value)
    elif isinstance(parent_value, list):
        for i, value in enumerate(parent_value):
            yield _proccess_list(parent_key, i, value)
    else:
        yield parent_key, parent_value
