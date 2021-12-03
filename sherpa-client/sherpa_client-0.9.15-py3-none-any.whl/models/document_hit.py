from typing import Any, Dict, Type, TypeVar

import attr

from ..models.document import Document

T = TypeVar("T", bound="DocumentHit")


@attr.s(auto_attribs=True)
class DocumentHit:
    """ """

    score: float
    id: str
    document: Document

    def to_dict(self) -> Dict[str, Any]:
        score = self.score
        id = self.id
        document = self.document.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "score": score,
                "_id": id,
                "document": document,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        score = d.pop("score")

        id = d.pop("_id")

        document = Document.from_dict(d.pop("document"))

        document_hit = cls(
            score=score,
            id=id,
            document=document,
        )

        return document_hit
