from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="EngineConfig")


@attr.s(auto_attribs=True)
class EngineConfig:
    """ """

    type: str
    name: str

    def to_dict(self) -> Dict[str, Any]:
        type = self.type
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "type": type,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = d.pop("type")

        name = d.pop("name")

        engine_config = cls(
            type=type,
            name=name,
        )

        return engine_config
