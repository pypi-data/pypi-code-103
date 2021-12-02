from typing import Any, Dict, Type, TypeVar

import attr

from ..models.search_total_relation import SearchTotalRelation

T = TypeVar("T", bound="SearchTotal")


@attr.s(auto_attribs=True)
class SearchTotal:
    """ """

    value: int
    relation: SearchTotalRelation

    def to_dict(self) -> Dict[str, Any]:
        value = self.value
        relation = self.relation.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "value": value,
                "relation": relation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        value = d.pop("value")

        relation = SearchTotalRelation(d.pop("relation"))

        search_total = cls(
            value=value,
            relation=relation,
        )

        return search_total
