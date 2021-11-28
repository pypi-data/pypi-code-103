"""Includes the supermodels decorator and namespace methods."""
import inspect
import json
import types
from collections import deque
from dataclasses import asdict, dataclass, field, fields, is_dataclass, make_dataclass
from datetime import datetime
from typing import Any, Optional

from supermodels.exceptions import ValidationError
from supermodels.fields import (
    FieldTypeChecker,
    ImmutableDict,
    ImmutableList,
    ImmutableSet,
    timestamp_field,
    version_field,
)
from supermodels.serdes import (
    DataModelDeserializer,
    DataModelSerializer,
    FieldDeserializer,
)
from supermodels.util import get_class_members, get_timestamp, is_supermodel


def validate_rules(self):
    """Validates supermodel instance data against field rules."""
    fails = []

    for own_field in fields(self):
        value = getattr(self, own_field.name)
        rules = own_field.metadata.get("rules", None)

        if rules:
            rule_fails = rules.validate(value)
            fails.extend(
                [
                    f"{own_field.name}_{rule_name}_{rule_value}"
                    for rule_name, rule_value in rule_fails
                ]
            )

    if not fails:
        return

    msg = "Failing rules: " + "; ".join(fails)
    self.raise_validation_error(msg)


def freeze_iterables(self):
    """Freezes the iterable attributes of a supermodel."""
    mapper = {
        FieldTypeChecker.is_list: ImmutableList,
        FieldTypeChecker.is_set: ImmutableSet,
        FieldTypeChecker.is_dict: ImmutableDict,
    }

    for own_field in fields(self):
        for type_checker, wrapper in mapper.items():
            if type_checker(own_field.type):
                value = getattr(self, own_field.name)
                object.__setattr__(self, own_field.name, wrapper(value, self.__class__))
                break


def __post_init__(self):
    """Provides a post init hook for supermodel instances."""
    validate_rules(self)

    if self.__dataclass_params__.frozen:
        freeze_iterables(self)


def __help__(cls):
    """Returns a dictionary with names and docs for methods attached to the dataclass."""
    help_types = (types.FunctionType, types.MethodType)
    decorated = (property, classmethod, staticmethod)

    d = {}

    for attr_name in dir(cls):
        if attr_name[:1] == "_":
            continue

        attr = getattr(cls, attr_name)
        attr_type = type(attr)

        if attr_type in help_types or isinstance(attr, decorated):
            attr_doc = (attr.__doc__ or "").strip()
            d[attr_name] = attr_doc

    return d


def __type__(self):
    """Returns the type of the supermodel."""
    return f"{self.__class__.__name__}"


def get_qualified_type(cls):
    """Returns the qualified type of the supermodel."""
    module_name = cls.__module__

    def __qualified_type__(self):
        """Returns the qualified type of the model."""
        return f"{module_name}.{self.__type__}"

    return __qualified_type__


def __str__(self) -> str:
    """Returns a str representation of the model."""
    try:
        return f"{self.__qualified_type__}: {self.__value__}"
    except AttributeError:
        return repr(self)


def get_supermodel_fields(
    cls, versioned: bool, timestamped: bool
) -> list[tuple[str, type, field]]:
    """Returns the fields of the supermodel.

    These include the underlying dataclass fields
    plus extra version and timestamp fields
    if required per the supermodel options.
    """
    field_names = [field.name for field in fields(cls)]

    attrs = []

    if timestamped:
        for attr in ("_created", "_updated"):
            if attr not in field_names:
                attrs.append((attr, datetime, timestamp_field()))

    if versioned:
        if "_version" not in field_names:
            attrs.append(("_version", int, version_field()))

    attrs.extend([(field.name, field.type, field) for field in fields(cls)])

    return attrs


def demodel_data(
    cls_or_self, data: dict[str, Any], repr_only: Optional[bool] = False
) -> dict[str, Any]:
    """Returns a dict with all nested models converted to dicts."""
    result = {}

    for own_field in fields(cls_or_self):
        if repr_only and not own_field.repr:
            continue

        attr = own_field.name
        value = data.get(attr)

        if value is None:
            result[attr] = value
            continue

        iter_types = (list, tuple, set, frozenset, deque)
        is_iter = isinstance(value, iter_types)
        values = list(value) if is_iter else [value]

        for i, value in enumerate(values):
            if is_supermodel(value):
                values[i] = value.to_dict(repr_only=repr_only)
            elif is_dataclass(value):
                values[i] = asdict(value)

        result[attr] = values if is_iter else values[0]

    return result


def copy_data(cls, data: dict[str, Any]) -> dict[str, Any]:
    """Returns a copy of a data dict via the custom json decoder."""
    data = demodel_data(cls, data)
    payload = json.dumps(data, cls=DataModelSerializer)
    return DataModelDeserializer.deserialize(payload)


def from_dict(cls, data: dict[str, Any]):
    """Returns a model instance with the provided attributes."""
    data = copy_data(cls, data)

    for own_field in fields(cls):
        key = own_field.name

        if key not in data:
            continue

        value = data[key]
        deser = FieldDeserializer(own_field.type, value)
        data[key] = deser.get_deserialized_value()

    timestamp_attrs = ("_created", "_updated")
    has_timestamp_attrs = all(data.get(attr) for attr in timestamp_attrs)

    if cls._TIMESTAMPED and not has_timestamp_attrs:
        # If any of the timestamp attrs is missing,
        # and the supermodel is timestamped
        # all the timestamps needs to be regenerated
        now = get_timestamp()

        for attr in timestamp_attrs:
            data[attr] = now

    if cls._VERSIONED and not data.get("_version"):
        data["_version"] = 1

    return cls(**data)


def from_json(cls, payload: str):
    """Returns a model instance with data from a json payload."""
    data = DataModelDeserializer.deserialize(payload)
    return cls.from_dict(data)


def to_dict(self, repr_only: Optional[bool] = False) -> str:
    """Returns a dictionary with model attributes and values."""
    items = asdict(self)

    ignored_field_names = [
        own_field.name
        for own_field in fields(self)
        if (
            own_field.metadata.get("mask") is True or (repr_only and not own_field.repr)
        )
    ]

    data = {}

    for key in items:
        if key in ignored_field_names:
            continue

        value = getattr(self, key)

        if is_supermodel(value):
            data[key] = value.to_dict(repr_only=repr_only)
            continue

        if isinstance(value, (list, tuple, set)):
            if any(is_supermodel(x) for x in value):
                iterable = []

                for element in value:
                    if is_supermodel(element):
                        element = element.to_dict(repr_only=repr_only)

                    iterable.append(element)

                data[key] = type(value)(iterable)
                continue

        data[key] = items[key]

    return data


def to_json(self, repr_only: Optional[bool] = False) -> str:
    """Returns a json representation of the model."""
    data = self.to_dict(repr_only=repr_only)
    data = demodel_data(self, data, repr_only=repr_only)

    return DataModelSerializer.serialize(data)


def raise_validation_error(self, msg: str) -> None:
    """Raises a validation error for the model."""
    data = self.to_json(repr_only=True)

    msg = f"{msg.strip('!. ')} - {data}"
    raise ValidationError(self, msg)


def update(self, **kwargs):
    """Returns an copy of the model with updated attributes."""
    data = {field.name: getattr(self, field.name) for field in fields(self)}

    data.update(kwargs)

    if self._VERSIONED:
        data["_version"] = self._version + 1

    if self._TIMESTAMPED:
        data["_updated"] = get_timestamp()

    return type(self)(**data)


def supermodel(cls=None, **kwargs):
    """Provides the supermodel decorator for dataclasses."""

    def wrapper(cls):
        kwargs["frozen"] = kwargs.get("frozen", True)
        versioned = kwargs.pop("versioned", False)
        timestamped = kwargs.pop("timestamped", False)

        namespace = {member[0]: member[1] for member in get_class_members(cls)}
        namespace.update(
            dict(
                __post_init__=__post_init__,
                __help__=classmethod(__help__),
                __type__=property(__type__),
                __qualified_type__=property(get_qualified_type(cls)),
                __str__=__str__,
                update=update,
                from_dict=classmethod(from_dict),
                from_json=classmethod(from_json),
                to_dict=to_dict,
                to_json=to_json,
                raise_validation_error=raise_validation_error,
                _SUPERMODEL=True,
                _VERSIONED=versioned,
                _TIMESTAMPED=timestamped,
            )
        )

        dc = dataclass(cls, **kwargs)

        mro = inspect.getmro(cls)
        bases = tuple(c for c in mro if is_dataclass(c) and c != cls)

        return make_dataclass(
            dc.__name__,
            bases=bases,
            fields=get_supermodel_fields(cls, versioned, timestamped),
            namespace=namespace,
            **kwargs,
        )

    if cls is None:
        return wrapper

    return wrapper(cls)
