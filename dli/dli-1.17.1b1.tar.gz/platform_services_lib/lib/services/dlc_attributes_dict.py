from collections import UserDict
from typing import Mapping


class AttributesDict(UserDict):

    def __init__(self, *args, **kwargs):
        # recursively provide the rather silly attribute access
        data = {}

        for arg in args:
            data.update(arg)

        data.update(**kwargs)

        for key, value in data.items():
            if isinstance(value, Mapping):
                self.__dict__[key] = AttributesDict(value)
            else:
                self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        attributes = ' '.join([
            '{}={}'.format(k, v) for k,v in self.__dict__.items()
            if not k.startswith('_')
        ])

        return "{}({})".format(self.__class__.__name__, attributes)
