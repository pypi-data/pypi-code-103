from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.bucket import Bucket

T = TypeVar("T", bound="Aggregation")


@attr.s(auto_attribs=True)
class Aggregation:
    """ """

    name: str
    buckets: List[Bucket]

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        buckets = []
        for buckets_item_data in self.buckets:
            buckets_item = buckets_item_data.to_dict()

            buckets.append(buckets_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "buckets": buckets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        buckets = []
        _buckets = d.pop("buckets")
        for buckets_item_data in _buckets:
            buckets_item = Bucket.from_dict(buckets_item_data)

            buckets.append(buckets_item)

        aggregation = cls(
            name=name,
            buckets=buckets,
        )

        return aggregation
