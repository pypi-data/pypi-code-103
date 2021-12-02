from typing import Any, Dict, Type, TypeVar

import attr

from ..models.segment_context import SegmentContext

T = TypeVar("T", bound="SegmentContexts")


@attr.s(auto_attribs=True)
class SegmentContexts:
    """ """

    before: SegmentContext
    after: SegmentContext

    def to_dict(self) -> Dict[str, Any]:
        before = self.before.to_dict()

        after = self.after.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "before": before,
                "after": after,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        before = SegmentContext.from_dict(d.pop("before"))

        after = SegmentContext.from_dict(d.pop("after"))

        segment_contexts = cls(
            before=before,
            after=after,
        )

        return segment_contexts
