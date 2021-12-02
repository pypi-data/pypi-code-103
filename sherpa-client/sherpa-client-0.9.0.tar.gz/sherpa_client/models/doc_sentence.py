from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="DocSentence")


@attr.s(auto_attribs=True)
class DocSentence:
    """ """

    start: int
    end: int

    def to_dict(self) -> Dict[str, Any]:
        start = self.start
        end = self.end

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "start": start,
                "end": end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        start = d.pop("start")

        end = d.pop("end")

        doc_sentence = cls(
            start=start,
            end=end,
        )

        return doc_sentence
