from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.doc_annotation_status import DocAnnotationStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="DocAnnotation")


@attr.s(auto_attribs=True)
class DocAnnotation:
    """A document annotation"""

    label_name: str
    start: int
    end: int
    text: str
    identifier: Union[Unset, str] = UNSET
    status: Union[Unset, DocAnnotationStatus] = UNSET
    created_date: Union[Unset, str] = UNSET
    modified_date: Union[Unset, str] = UNSET
    created_by: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        label_name = self.label_name
        start = self.start
        end = self.end
        text = self.text
        identifier = self.identifier
        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        created_date = self.created_date
        modified_date = self.modified_date
        created_by = self.created_by

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "labelName": label_name,
                "start": start,
                "end": end,
                "text": text,
            }
        )
        if identifier is not UNSET:
            field_dict["identifier"] = identifier
        if status is not UNSET:
            field_dict["status"] = status
        if created_date is not UNSET:
            field_dict["createdDate"] = created_date
        if modified_date is not UNSET:
            field_dict["modifiedDate"] = modified_date
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label_name = d.pop("labelName")

        start = d.pop("start")

        end = d.pop("end")

        text = d.pop("text")

        identifier = d.pop("identifier", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, DocAnnotationStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = DocAnnotationStatus(_status)

        created_date = d.pop("createdDate", UNSET)

        modified_date = d.pop("modifiedDate", UNSET)

        created_by = d.pop("createdBy", UNSET)

        doc_annotation = cls(
            label_name=label_name,
            start=start,
            end=end,
            text=text,
            identifier=identifier,
            status=status,
            created_date=created_date,
            modified_date=modified_date,
            created_by=created_by,
        )

        return doc_annotation
