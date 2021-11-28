"""Includes shared utility methods for the supermodels package."""
import datetime
import inspect
import re
import uuid
from dataclasses import is_dataclass
from typing import Any, Pattern

from dateutil.relativedelta import relativedelta


def get_timestamp() -> datetime.datetime:
    """Returns a utc timestamp with seconds precision."""
    timestamp = datetime.datetime.utcnow()
    timestamp = timestamp + relativedelta(microseconds=-timestamp.microsecond)
    return timestamp


def get_uuid() -> uuid.UUID:
    """Returns a globally unique identifier."""
    return uuid.uuid4()


def get_datetime_pattern(datetime_format: str) -> Pattern[str]:
    """Returns a matching mattern that corresponds to a datetime format."""
    mapping = {
        "%Y": "[0-9]{4}",
        "%m": "[0-1][0-9]",
        "%d": "[0-3][0-9]",
        "%H": "[0-2][0-9]",
        "%M": "[0-5][0-9]",
        "%S": "[0-5][0-9]",
        "%f": "[0-9]{6}",
        "%y": "[0-9]{2}",
        "%G": "[0-9]{4}",
        "%I": "[0-1][0-9]",
        "%j": "[0-3][0-9]{2}",
        "%U": "[0-5][0-9]",
        "%V": "[0-5][0-9]",
        "%W": "[0-5][0-9]",
        "%u": "[1-7]",
        "%w": "[0-6]",
    }

    expr = datetime_format

    for key, value in mapping.items():
        expr = expr.replace(key, value)

    return re.compile(rf"{expr}")


def get_object_identifier(o: Any) -> str:
    """Returns the package-level identifier of the sender."""
    if is_supermodel(o):
        return o.__qualified_type__

    kind = o if inspect.isclass(o) else type(o)
    return f"{kind.__module__}.{kind.__qualname__}"


def get_class_members(cls: Any) -> tuple[str]:
    """Returns the own members of a class, incl. overrides."""
    dundr_attrs = ("__setattr__", "__getattr__", "__delattr__")
    methods = [
        member
        for member in inspect.getmembers(cls, predicate=inspect.ismethod(cls))
        if member[0] not in dundr_attrs + ("__init__",)
        if not inspect.isbuiltin(member[1])
        if not inspect.ismemberdescriptor(member[1])
        if hasattr(member[1], "__qualname__")
        if member[1].__qualname__.split("<locals>.")[-1].split(".")[0] == cls.__name__
    ]

    decorated = inspect.getmembers(
        cls, lambda x: isinstance(x, (property, classmethod, staticmethod))
    )

    return methods + decorated


def is_supermodel(obj: Any) -> bool:
    """Returns True if the obj is a supermodel or an instance of a supermodel."""
    cls = obj if isinstance(obj, type) else type(obj)
    return is_dataclass(cls) and hasattr(cls, "_SUPERMODEL")


def is_versioned(obj: Any) -> bool:
    """Returns True if the obj is a supermodel and is versioned."""
    return is_supermodel(obj) and obj._VERSIONED


def is_timestamped(obj: Any) -> bool:
    """Returns True if the obj is a supermodel and is timestamped."""
    return is_supermodel(obj) and obj._TIMESTAMPED
