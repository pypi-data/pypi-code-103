from typing import Generator

from district42 import GenericSchema
from multidict import MultiDict

__all__ = ("get_unique_keys",)


def get_unique_keys(multidict_: MultiDict[GenericSchema]) -> Generator[str, None, None]:
    used = set()
    for key in multidict_.keys():
        if key in used:
            continue
        yield key
        used.add(key)
