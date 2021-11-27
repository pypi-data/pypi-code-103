from dataclasses import dataclass
from typing import Optional, List, Iterator, Type

from marshy.types import ExternalItemType

from schemey.json_output_context import JsonOutputContext
from schemey.schema_abc import SchemaABC, T
from schemey.schema_error import SchemaError


@dataclass(frozen=True)
class EnumSchema(SchemaABC[T]):
    _item_type: Type[T]
    default_value: Optional[T] = None

    @property
    def item_type(self):
        return self._item_type

    def get_schema_errors(self, item: T, current_path: Optional[List[str]] = None) -> Iterator[SchemaError]:
        if not isinstance(item, self.item_type) and not next((i for i in self.item_type if i.value == item), None):
            yield SchemaError(current_path or [], 'value_not_permitted', item)

    def to_json_schema(self, json_output_context: Optional[JsonOutputContext] = None) -> Optional[ExternalItemType]:
        json_schema = dict(enum=[i.value for i in self.item_type])
        if self.default_value:
            json_schema['default'] = self.default_value.value
        return json_schema
