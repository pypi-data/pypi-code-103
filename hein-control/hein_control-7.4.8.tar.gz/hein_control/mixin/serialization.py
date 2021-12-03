"""mixins for ensuring/verifying JSON serializability"""

import json
from abc import ABC, abstractmethod
from typing import Union, Any


def is_jsonable(obj) -> bool:
    """verifies that the provided object is JSON serializable"""
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False


class DumpableState(ABC):
    """a dumpable object which can be represented as a dictionary"""

    @abstractmethod
    def as_dict(self) -> dict:
        """represents the state or properties as a serializable object"""
        raise NotImplementedError


class DumpableList(ABC):
    """a dumpable object which can be represented as a list"""

    @abstractmethod
    def as_list(self) -> list:
        """if the dumpable is iterable, represents the list as a list"""
        raise NotImplementedError


def serializable_cast(incoming: Union[DumpableState, DumpableList]) -> Union[Any, list, dict]:
    """attempts to cast a DumpableState or DumpableList to serializable"""
    if is_jsonable(incoming):
        return incoming
    elif isinstance(incoming, DumpableList):
        return incoming.as_list()
    elif isinstance(incoming, DumpableState):
        return incoming.as_dict()
    else:
        raise TypeError(f'the provided object type "{type(incoming)}" could not be made serializable')


def make_iterable_serializable(*obj: Union[DumpableState, DumpableList, Any]) -> list:
    """
    Attempts to ensure that the provided object(s) are serializable.

    :param obj: objects to ensure are serializable
    :return: serializable object
    """
    out = []
    for o in obj:
        # if it's serializable, directly append
        if is_jsonable(o) is True:
            out.append(o)
        else:  # otherwise attempt cast
            out.append(serializable_cast(o))
    return out


def make_mapping_serializable(**objs) -> dict:
    """
    Attempts to ensure that the provided object(s) are serializable

    :param objs: key-object mappings
    :return: serializable dictionary
    """
    out = {}
    for key, obj in objs.items():
        if is_jsonable(obj):
            out[key] = obj
        else:
            out[key] = serializable_cast(obj)
    return out
