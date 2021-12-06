from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.http_service_metadata import HttpServiceMetadata
from ..types import UNSET, Unset

T = TypeVar("T", bound="HttpServiceRecord")


@attr.s(auto_attribs=True)
class HttpServiceRecord:
    """ """

    name: str
    host: str
    port: int
    metadata: HttpServiceMetadata
    ssl: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        host = self.host
        port = self.port
        metadata = self.metadata.to_dict()

        ssl = self.ssl

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "host": host,
                "port": port,
                "metadata": metadata,
            }
        )
        if ssl is not UNSET:
            field_dict["ssl"] = ssl

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        host = d.pop("host")

        port = d.pop("port")

        metadata = HttpServiceMetadata.from_dict(d.pop("metadata"))

        ssl = d.pop("ssl", UNSET)

        http_service_record = cls(
            name=name,
            host=host,
            port=port,
            metadata=metadata,
            ssl=ssl,
        )

        return http_service_record
