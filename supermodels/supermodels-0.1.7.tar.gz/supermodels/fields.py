"""Includes special field types and field type checks."""
import re
from dataclasses import field, is_dataclass
from enum import EnumMeta
from types import GenericAlias, UnionType
from typing import Any, Callable, Pattern, _GenericAlias, _UnionGenericAlias

from supermodels.exceptions import ImmutableFieldError
from supermodels.util import get_timestamp, get_uuid, is_supermodel


masked_field = lambda: field(metadata=dict(mask=True), kw_only=True)
uuid_field = lambda: field(default_factory=get_uuid, kw_only=True)
timestamp_field = lambda: field(default_factory=get_timestamp, repr=False, kw_only=True)
version_field = lambda: field(default_factory=lambda: 1, repr=False, kw_only=True)


class FieldTypeChecker:
    """Provides a dataclass field type checker service."""

    @classmethod
    def _get_iter_type(cls, field_type: Any) -> Any:
        """Returns the builtint type name for a dataclass field_type."""
        type_name = str(field_type).split("[")[0].lower()
        type_name = type_name.split(".")[-1]
        return eval(type_name)

    @classmethod
    def _is_iter(cls, field_type: Any) -> bool:
        """Returns true if the dataclass field type is an iterable."""
        return type(field_type) in (_GenericAlias, GenericAlias)

    @classmethod
    def _is_iter_type(cls, field_type: Any, iter_type: Any) -> bool:
        """Returns true if the dataclass field type matches the provided type."""
        return cls._is_iter(field_type) and cls._get_iter_type(field_type) == iter_type

    @staticmethod
    def is_dataclass(field_type: Any) -> bool:
        """Returns true if the field type is a dataclass but not a supermodel."""
        return is_dataclass(field_type) and not is_supermodel(field_type)

    @classmethod
    def is_dict(cls, field_type: Any) -> bool:
        """Returns true if the field type is a dict."""
        return cls._is_iter_type(field_type, dict)

    @staticmethod
    def is_enum(field_type: Any) -> bool:
        """Returns true if the field type is EnumMeta."""
        return type(field_type) == EnumMeta

    @classmethod
    def is_frozenset(cls, field_type: Any) -> bool:
        """Returns true if the field type is a frozenset."""
        return cls._is_iter_type(field_type, frozenset)

    @classmethod
    def is_list(cls, field_type: Any) -> bool:
        """Returns true if the field type is a list."""
        return cls._is_iter_type(field_type, list)

    @staticmethod
    def is_pattern(field_type: Any) -> bool:
        """Returns true if the field type is a regex pattern."""
        return field_type in (re.Pattern, Pattern)

    @classmethod
    def is_set(cls, field_type: Any) -> bool:
        """Returns true if the field type is a set."""
        return cls._is_iter_type(field_type, set)

    @staticmethod
    def is_supermodel(field_type: Any) -> bool:
        """Returns true if the field type is a supermodel."""
        return is_supermodel(field_type)

    @classmethod
    def is_tuple(cls, field_type: Any) -> bool:
        """Returns true if the field type is a tuple."""
        return cls._is_iter_type(field_type, tuple)

    @staticmethod
    def is_union(field_type: Any) -> bool:
        """Returns true if the field type is a union."""
        return type(field_type) in (_UnionGenericAlias, UnionType)


class ImmutableIterMixin:
    """Provides common capabilities for immutable iterable classes."""

    def freeze_attrs(self) -> None:
        """Freezes all methods of the iterable that can make changes to it."""
        for attr in self.__FROZEN_ATTRS__:
            object.__setattr__(self, attr, self.__override__(attr))

    def __override__(self, attr: str) -> Callable:
        """Returns an intercept method for a frozen attribute."""
        context = f"Method {attr}"

        def intercept(*args, **kwargs):
            self.__raise__(context)

        return intercept

    def __raise__(self, context: str) -> None:
        """Raises a frozen field error when a frozen attribute is invoked."""
        msg = f"{context} is disabled for supermodel {self.__TYPE__} fields."
        sender = self.model
        raise ImmutableFieldError(sender, msg)


class ImmutableDict(dict, ImmutableIterMixin):
    """Provides a dict wrapper that makes it immutable."""

    __FROZEN_ATTRS__ = ("clear", "pop", "popitem", "update")
    __TYPE__ = "dict"

    def __init__(self, items=None, model=None):
        """Overrides the __init__ method of dict to make it immutable."""
        self.model = model
        super().__init__(items)
        self.freeze_attrs()

    def __delitem__(self, *args, **kwargs) -> None:
        """Freezes the __delitem__ attribute."""
        msg = "The del operator"
        self.__raise__(msg)

    def __setitem__(self, *args, **kwargs) -> None:
        """Freezes the __setitem__ attribute."""
        msg = "Item assignment"
        self.__raise__(msg)


class ImmutableList(list, ImmutableIterMixin):
    """Provides a list wrapper that makes it immutable."""

    __FROZEN_ATTRS__ = (
        "append",
        "clear",
        "extend",
        "insert",
        "pop",
        "remove",
        "reverse",
    )
    __TYPE__ = "list"

    def __init__(self, elements=None, model=None):
        """Overrides the __init__ method of list to make it immutable."""
        self.model = model
        super().__init__(elements)
        self.freeze_attrs()

    def __delitem__(self, *args, **kwargs) -> None:
        """Freezes the __delitem__ attribute."""
        msg = "Deleting elements"
        self.__raise__(msg)

    def __setitem__(self, *args, **kwargs) -> None:
        """Freezes the __delitem__ attribute."""
        msg = "Adding elements"
        self.__raise__(msg)


class ImmutableSet(set, ImmutableIterMixin):
    """Provides a set wrapper that makes it immutable."""

    __FROZEN_ATTRS__ = ("add", "clear", "discard", "pop", "remove", "update")
    __TYPE__ = "set"

    def __init__(self, elements=None, model=None):
        """Overrides the __init__ method of set to make it immutable."""
        self.model = model
        super().__init__(elements)
        self.freeze_attrs()

    def __delitem__(self, *args, **kwargs) -> None:
        """Freezes the __delitem__ attribute."""
        msg = "Deleting elements"
        self.__raise__(msg)

    def __setitem__(self, *args, **kwargs) -> None:
        """Freezes the __delitem__ attribute."""
        msg = "Adding elements"
        self.__raise__(msg)
