from typing import Generator

from district42 import GenericSchema
from multidict import CIMultiDict

__all__ = ("get_unique_keys",)


def get_unique_keys(multidict_: CIMultiDict[GenericSchema]) -> Generator[str, None, None]:
    used = set()
    for key in multidict_.keys():
        if key.lower() in used:
            continue
        yield key
        used.add(key.lower())
