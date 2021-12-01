from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional, List, Union, Tuple
from .with_properties import WithProperties


@dataclass
class CreateDataset(dict, WithProperties):
    name: Optional[str] = None
    connectionId: Optional[int] = None
    connectionName: Optional[str] = None
    files: Optional[List[str]] = None
    folders: Optional[List[str]] = None
    data_properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None

    def _create_with_property(self, data_properties: Tuple[str, str]):
        key, value = data_properties
        return self.with_property(key, value)

    def _create_with_properties(self, data_properties: List[Tuple[str, str]]):
        return self.with_properties(properties=data_properties)

    def add_properties(
        self, data_properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None
    ) -> CreateDataset:
        if data_properties and isinstance(data_properties, list):
            self._create_with_properties(data_properties=data_properties)
        elif data_properties and isinstance(data_properties, tuple):
            self._create_with_property(data_properties=data_properties)
        return self

    def as_dict(self):
        return asdict(self)
