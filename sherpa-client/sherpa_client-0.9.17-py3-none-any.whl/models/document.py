from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.doc_annotation import DocAnnotation
from ..models.doc_category import DocCategory
from ..models.doc_sentence import DocSentence
from ..models.document_metadata import DocumentMetadata
from ..types import UNSET, Unset

T = TypeVar("T", bound="Document")


@attr.s(auto_attribs=True)
class Document:
    """ """

    identifier: str
    title: str
    text: str
    metadata: Union[Unset, DocumentMetadata] = UNSET
    sentences: Union[Unset, List[DocSentence]] = UNSET
    categories: Union[Unset, List[DocCategory]] = UNSET
    annotations: Union[Unset, List[DocAnnotation]] = UNSET
    created_date: Union[Unset, str] = UNSET
    modified_date: Union[Unset, str] = UNSET
    created_by: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier
        title = self.title
        text = self.text
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        sentences: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.sentences, Unset):
            sentences = []
            for sentences_item_data in self.sentences:
                sentences_item = sentences_item_data.to_dict()

                sentences.append(sentences_item)

        categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.categories, Unset):
            categories = []
            for categories_item_data in self.categories:
                categories_item = categories_item_data.to_dict()

                categories.append(categories_item)

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
                "title": title,
                "text": text,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if sentences is not UNSET:
            field_dict["sentences"] = sentences
        if categories is not UNSET:
            field_dict["categories"] = categories
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

        title = d.pop("title")

        text = d.pop("text")

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, DocumentMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = DocumentMetadata.from_dict(_metadata)

        sentences = []
        _sentences = d.pop("sentences", UNSET)
        for sentences_item_data in _sentences or []:
            sentences_item = DocSentence.from_dict(sentences_item_data)

            sentences.append(sentences_item)

        categories = []
        _categories = d.pop("categories", UNSET)
        for categories_item_data in _categories or []:
            categories_item = DocCategory.from_dict(categories_item_data)

            categories.append(categories_item)

        annotations = []
        _annotations = d.pop("annotations", UNSET)
        for annotations_item_data in _annotations or []:
            annotations_item = DocAnnotation.from_dict(annotations_item_data)

            annotations.append(annotations_item)

        created_date = d.pop("createdDate", UNSET)

        modified_date = d.pop("modifiedDate", UNSET)

        created_by = d.pop("createdBy", UNSET)

        document = cls(
            identifier=identifier,
            title=title,
            text=text,
            metadata=metadata,
            sentences=sentences,
            categories=categories,
            annotations=annotations,
            created_date=created_date,
            modified_date=modified_date,
            created_by=created_by,
        )

        return document
