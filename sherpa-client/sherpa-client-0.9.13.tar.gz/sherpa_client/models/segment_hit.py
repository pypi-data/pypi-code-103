from typing import Any, Dict, Type, TypeVar

import attr

from ..models.segment import Segment

T = TypeVar("T", bound="SegmentHit")


@attr.s(auto_attribs=True)
class SegmentHit:
    """ """

    score: float
    id: str
    segment: Segment

    def to_dict(self) -> Dict[str, Any]:
        score = self.score
        id = self.id
        segment = self.segment.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "score": score,
                "_id": id,
                "segment": segment,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        score = d.pop("score")

        id = d.pop("_id")

        segment = Segment.from_dict(d.pop("segment"))

        segment_hit = cls(
            score=score,
            id=id,
            segment=segment,
        )

        return segment_hit
