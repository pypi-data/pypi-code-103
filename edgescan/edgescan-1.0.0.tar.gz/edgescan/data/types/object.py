from dataclasses import dataclass
from edgescan.constants import DEFAULT_INDENT, SORT_KEYS_BY_DEFAULT, REMOVE_EMPTY_VALUES_BY_DEFAULT

import hodgepodge.types


@dataclass(frozen=True)
class Object:
    id: int

    def to_dict(self, remove_empty_values: bool = REMOVE_EMPTY_VALUES_BY_DEFAULT):
        return hodgepodge.types.dataclass_to_dict(data=self, remove_empty_values=remove_empty_values)

    def to_json(
            self,
            indent: int = DEFAULT_INDENT,
            sort_keys: bool = SORT_KEYS_BY_DEFAULT,
            remove_empty_values: bool = REMOVE_EMPTY_VALUES_BY_DEFAULT):

        data = self.to_dict(remove_empty_values=remove_empty_values)
        return hodgepodge.types.dict_to_json(
            data=data,
            indent=indent,
            sort_keys=sort_keys,
            remove_empty_values=remove_empty_values,
        )

    def __hash__(self):
        return self.id

