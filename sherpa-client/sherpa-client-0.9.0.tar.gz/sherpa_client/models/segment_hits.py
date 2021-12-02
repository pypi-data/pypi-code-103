from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.aggregation import Aggregation
from ..models.search_total import SearchTotal
from ..models.segment_hit import SegmentHit
from ..types import UNSET, Unset

T = TypeVar("T", bound="SegmentHits")


@attr.s(auto_attribs=True)
class SegmentHits:
    """ """

    total: SearchTotal
    hits: List[SegmentHit]
    max_score: Union[Unset, float] = UNSET
    aggregations: Union[Unset, List[Aggregation]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        total = self.total.to_dict()

        hits = []
        for hits_item_data in self.hits:
            hits_item = hits_item_data.to_dict()

            hits.append(hits_item)

        max_score = self.max_score
        aggregations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.aggregations, Unset):
            aggregations = []
            for aggregations_item_data in self.aggregations:
                aggregations_item = aggregations_item_data.to_dict()

                aggregations.append(aggregations_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "total": total,
                "hits": hits,
            }
        )
        if max_score is not UNSET:
            field_dict["max_score"] = max_score
        if aggregations is not UNSET:
            field_dict["aggregations"] = aggregations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        total = SearchTotal.from_dict(d.pop("total"))

        hits = []
        _hits = d.pop("hits")
        for hits_item_data in _hits:
            hits_item = SegmentHit.from_dict(hits_item_data)

            hits.append(hits_item)

        max_score = d.pop("max_score", UNSET)

        aggregations = []
        _aggregations = d.pop("aggregations", UNSET)
        for aggregations_item_data in _aggregations or []:
            aggregations_item = Aggregation.from_dict(aggregations_item_data)

            aggregations.append(aggregations_item)

        segment_hits = cls(
            total=total,
            hits=hits,
            max_score=max_score,
            aggregations=aggregations,
        )

        return segment_hits
