from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.doc_annotation import DocAnnotation
from ..models.segment_metadata import SegmentMetadata
from ..types import UNSET, Unset

T = TypeVar("T", bound="Segment")


@attr.s(auto_attribs=True)
class Segment:
    """ """

    identifier: str
    document_identifier: str
    document_title: str
    text: str
    start: int
    end: int
    shift: Union[Unset, int] = UNSET
    metadata: Union[Unset, SegmentMetadata] = UNSET
    annotations: Union[Unset, List[DocAnnotation]] = UNSET
    created_date: Union[Unset, str] = UNSET
    modified_date: Union[Unset, str] = UNSET
    created_by: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier
        document_identifier = self.document_identifier
        document_title = self.document_title
        text = self.text
        start = self.start
        end = self.end
        shift = self.shift
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        annotations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.annotations, Unset):
            annotations = []
            for annotations_item_data in self.annotations:
                annotations_item = annotations_item_data.to_dict()

                annotations.append(annotations_item)

        created_date = self.created_date
        modified_date = self.modified_date
        created_by = self.created_by

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "identifier": identifier,
                "documentIdentifier": document_identifier,
                "documentTitle": document_title,
                "text": text,
                "start": start,
                "end": end,
            }
        )
        if shift is not UNSET:
            field_dict["shift"] = shift
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if annotations is not UNSET:
            field_dict["annotations"] = annotations
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
        identifier = d.pop("identifier")

        document_identifier = d.pop("documentIdentifier")

        document_title = d.pop("documentTitle")

        text = d.pop("text")

        start = d.pop("start")

        end = d.pop("end")

        shift = d.pop("shift", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, SegmentMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = SegmentMetadata.from_dict(_metadata)

        annotations = []
        _annotations = d.pop("annotations", UNSET)
        for annotations_item_data in _annotations or []:
            annotations_item = DocAnnotation.from_dict(annotations_item_data)

            annotations.append(annotations_item)

        created_date = d.pop("createdDate", UNSET)

        modified_date = d.pop("modifiedDate", UNSET)

        created_by = d.pop("createdBy", UNSET)

        segment = cls(
            identifier=identifier,
            document_identifier=document_identifier,
            document_title=document_title,
            text=text,
            start=start,
            end=end,
            shift=shift,
            metadata=metadata,
            annotations=annotations,
            created_date=created_date,
            modified_date=modified_date,
            created_by=created_by,
        )

        return segment
