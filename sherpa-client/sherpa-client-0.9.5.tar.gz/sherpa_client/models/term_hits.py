from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.search_total import SearchTotal
from ..models.term_hit import TermHit
from ..types import UNSET, Unset

T = TypeVar("T", bound="TermHits")


@attr.s(auto_attribs=True)
class TermHits:
    """ """

    total: SearchTotal
    hits: List[TermHit]
    max_score: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        total = self.total.to_dict()

        hits = []
        for hits_item_data in self.hits:
            hits_item = hits_item_data.to_dict()

            hits.append(hits_item)

        max_score = self.max_score

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "total": total,
                "hits": hits,
            }
        )
        if max_score is not UNSET:
            field_dict["max_score"] = max_score

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        total = SearchTotal.from_dict(d.pop("total"))

        hits = []
        _hits = d.pop("hits")
        for hits_item_data in _hits:
            hits_item = TermHit.from_dict(hits_item_data)

            hits.append(hits_item)

        max_score = d.pop("max_score", UNSET)

        term_hits = cls(
            total=total,
            hits=hits,
            max_score=max_score,
        )

        return term_hits
