from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.segment import Segment
from ..types import UNSET, Unset

T = TypeVar("T", bound="SegmentContext")


@attr.s(auto_attribs=True)
class SegmentContext:
    """ """

    size: int
    segments: Union[Unset, List[Segment]] = UNSET
    merged: Union[Unset, Segment] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        size = self.size
        segments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.segments, Unset):
            segments = []
            for segments_item_data in self.segments:
                segments_item = segments_item_data.to_dict()

                segments.append(segments_item)

        merged: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.merged, Unset):
            merged = self.merged.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "size": size,
            }
        )
        if segments is not UNSET:
            field_dict["segments"] = segments
        if merged is not UNSET:
            field_dict["merged"] = merged

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        size = d.pop("size")

        segments = []
        _segments = d.pop("segments", UNSET)
        for segments_item_data in _segments or []:
            segments_item = Segment.from_dict(segments_item_data)

            segments.append(segments_item)

        _merged = d.pop("merged", UNSET)
        merged: Union[Unset, Segment]
        if isinstance(_merged, Unset):
            merged = UNSET
        else:
            merged = Segment.from_dict(_merged)

        segment_context = cls(
            size=size,
            segments=segments,
            merged=merged,
        )

        return segment_context
