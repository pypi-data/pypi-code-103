"""Common classes and methods used in framework."""
from collections.abc import Generator
from typing import Any

class ContainerField:
    """Common class for Form and Serializer."""
    def __init__(self, source: str | None = None):
        self.source = source

class Container:
    FIELD_BASE_CLASS = ContainerField
    RESERVED_ATTRS: list[str] = []

    def __init__(self, *args: tuple, **kwargs: dict) -> None: # pylint: disable=unused-argument
        # List of declared fields
        self._field_names = [
            attribute
            for attribute in dir(self)
            if attribute not in self.RESERVED_ATTRS and isinstance(getattr(self, attribute), self.FIELD_BASE_CLASS)
        ]

    def _field_values(self, data: Any) -> Generator:
        for field_name in self._field_names:
            field: ContainerField = getattr(self, field_name)
            field_source = getattr(field, 'source', None)  # Using field's `source` attribute as value path
            property_value_path = field_source or field_name
            field_value = get_property_value(data, property_value_path)
            yield field_name, field_value, field

def get_property_value(entity: dict | object, key: str) -> Any:
    """Get value by key from dict or any object.

    Returns None if key missing in entity
    """
    if isinstance(entity, dict):
        return entity.get(key, None)

    return getattr(entity, key, None)
