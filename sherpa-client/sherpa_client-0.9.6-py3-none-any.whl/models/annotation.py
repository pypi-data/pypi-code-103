from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.annotation_status import AnnotationStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="Annotation")


@attr.s(auto_attribs=True)
class Annotation:
    """A document annotation"""

    document_identifier: str
    label_name: str
    start: int
    end: int
    text: str
    status: Union[Unset, AnnotationStatus] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        document_identifier = self.document_identifier
        label_name = self.label_name
        start = self.start
        end = self.end
        text = self.text
        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "documentIdentifier": document_identifier,
                "labelName": label_name,
                "start": start,
                "end": end,
                "text": text,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        document_identifier = d.pop("documentIdentifier")

        label_name = d.pop("labelName")

        start = d.pop("start")

        end = d.pop("end")

        text = d.pop("text")

        _status = d.pop("status", UNSET)
        status: Union[Unset, AnnotationStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = AnnotationStatus(_status)

        annotation = cls(
            document_identifier=document_identifier,
            label_name=label_name,
            start=start,
            end=end,
            text=text,
            status=status,
        )

        return annotation
