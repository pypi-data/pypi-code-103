"""Includes serializers and deserializers for supermodels and their fields."""
import functools
import json
import re
from collections import deque
from dataclasses import dataclass, Field, is_dataclass
from datetime import datetime
from enum import EnumMeta
from uuid import UUID
from typing import Any, Callable, get_args, Pattern, Type

from supermodels.config import TIMESTAMP_FORMAT
from supermodels.fields import FieldTypeChecker
from supermodels.util import get_datetime_pattern, is_supermodel

RE_TIMESTAMP = get_datetime_pattern(TIMESTAMP_FORMAT)
RE_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def if_type(t):
    """Provides a decorator that sense-checks the input to deser type check methods."""

    def wrapper(func):
        @functools.wraps(func)
        def wrapped(self, value: Any, *args, **kwargs) -> bool:
            if not isinstance(value, t):
                return False
            return func(self, value, *args, **kwargs)

        return wrapped

    return wrapper


class DataModelSerializer(json.JSONEncoder):
    """A custom serializer for supermodels."""

    ENCODERS: dict[Type[Any], Callable[[Any], Any]] = {
        datetime: lambda x: x.strftime(TIMESTAMP_FORMAT),
        deque: list,
        EnumMeta: lambda x: x.value,
        frozenset: list,
        re.Pattern: lambda x: x.pattern,
        set: list,
        UUID: str,
    }

    @classmethod
    def serialize(cls, data: dict[str, Any]) -> str:
        """Returns a json representation of the model data."""
        return json.dumps(data, cls=cls)

    def default(self, obj: Any) -> Any:
        """Overrides the default json encoder."""
        field_type = type(obj)

        if isinstance(field_type, EnumMeta):
            field_type = EnumMeta

        try:
            mapper = self.ENCODERS[field_type]
            return mapper(obj)
        except KeyError:
            pass

        return json.JSONEncoder.default(self, obj)


class DataModelDeserializer(json.JSONDecoder):
    """A custom json deserializer for supermodels."""

    DECODERS: dict[Any, tuple[Pattern[str], Callable[[Any], Any]]] = {
        datetime: (RE_TIMESTAMP, lambda x: datetime.strptime(x, TIMESTAMP_FORMAT)),
        UUID: (RE_UUID, lambda x: UUID(x)),
    }

    @classmethod
    def deserialize(cls, payload: str) -> dict[str, Any]:
        """Returns a data dictionary with the parsed json payload."""
        return json.loads(payload, cls=cls)

    def __init__(self, *args, **kwargs):
        """Creates an instance of the deserializer."""
        options = dict(object_hook=self.object_hook)
        kwargs.update(options)
        super().__init__(*args, **kwargs)

    def object_hook(self, data: dict[str, Any]) -> dict[str, Any]:
        """Provides a custom object hook for the json decoder."""
        for key, value in data.items():
            for pattern, mapper in self.DECODERS.values():
                if self.test_value(value, pattern):
                    data[key] = mapper(value)
                    break

        return data

    @if_type(str)
    def test_value(self, value: Any, pattern: Pattern[str]) -> bool:
        """Returns True if the value matches the pattern."""
        return pattern.match(value) is not None


class FieldDeserializer:
    """Provides a type-aware deserializer for supermodel field data."""

    def __init__(self, field_type: Field, value: Any):
        """Creates an instance of the field deserializer."""
        self.field_type = field_type
        self.value = value

    def get_deserialized_value(self):
        """Deserializes the field."""
        field_type = self.field_type
        value = self.value

        ftc = FieldTypeChecker
        mapper = {
            ftc.is_dataclass: self.deserialize_dataclass,
            ftc.is_dict: self.deserialize_dict,
            ftc.is_enum: self.deserialize_enum,
            ftc.is_frozenset: self.deserialize_frozenset,
            ftc.is_list: self.deserialize_list,
            ftc.is_pattern: self.deserialize_pattern,
            ftc.is_set: self.deserialize_set,
            ftc.is_supermodel: self.deserialize_dataclass,
            ftc.is_tuple: self.deserialize_tuple,
            ftc.is_union: self.deserialize_union,
        }

        for type_check, deser in mapper.items():
            if type_check(field_type):
                return deser()

        return value

    def deserialize_item(self, item: Any, dc: dataclass) -> Any:
        """Returns a dataclass instance of a dict."""
        if not isinstance(item, dict):
            return item
        elif is_supermodel(dc):
            return dc.from_dict(item)
        else:
            return dc(**item)

    def deserialize_dataclass(self) -> None:
        """Converts dataclass-type attribute value to a dataclass."""
        return self.deserialize_item(self.value, self.field_type)

    def deserialize_dict(self) -> None:
        """Returns a dict with resolved value types."""
        values = {}
        dc = get_args(self.field_type)[1]

        for key, value in self.value.items():
            values[key] = self.deserialize_item(value, dc)

        return values

    def deserialize_enum(self) -> None:
        """Converts enum values to enum attributes."""
        return self.field_type(self.value)

    def deserialize_frozenset(self) -> None:
        """Returns a frozenset instance with resolved element types."""
        return frozenset(self.deserialize_list())

    def deserialize_list(self) -> None:
        """Returns a list with resolved element types."""
        values = []
        dc = get_args(self.field_type)[0]

        for value in self.value:
            value = self.deserialize_item(value, dc)
            values.append(value)

        return values

    def deserialize_pattern(self) -> None:
        """Retruns a compiled regex pattern with value as the expression."""
        return re.compile(rf"{self.value}")

    def deserialize_set(self) -> None:
        """Returns a set with resolved element types."""
        return set(self.deserialize_list())

    def deserialize_tuple(self) -> None:
        """Returns a tuple with resolved element types."""
        values = []
        args = get_args(self.field_type)

        for i, arg in enumerate(args):
            value = self.deserialize_item(self.value[i], arg)
            values.append(value)

        return tuple(values)

    def deserialize_union(self) -> None:
        """Converts the value of a Union-type attribute value to a dataclass, if applicable."""
        args = get_args(self.field_type)
        dc_args = [arg for arg in args if is_dataclass(arg)]

        for dc in dc_args:
            try:
                return self.deserialize_item(self.value, dc)
            except TypeError:
                continue

        return self.value
