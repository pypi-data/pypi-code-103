from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.annotated_doc_annotation import AnnotatedDocAnnotation
from ..models.annotated_doc_category import AnnotatedDocCategory
from ..models.annotated_document_metadata import AnnotatedDocumentMetadata
from ..models.doc_sentence import DocSentence
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnnotatedDocument")


@attr.s(auto_attribs=True)
class AnnotatedDocument:
    """ """

    text: str
    identifier: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    metadata: Union[Unset, AnnotatedDocumentMetadata] = UNSET
    sentences: Union[Unset, List[DocSentence]] = UNSET
    categories: Union[Unset, List[AnnotatedDocCategory]] = UNSET
    annotations: Union[Unset, List[AnnotatedDocAnnotation]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        text = self.text
        identifier = self.identifier
        title = self.title
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

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "text": text,
            }
        )
        if identifier is not UNSET:
            field_dict["identifier"] = identifier
        if title is not UNSET:
            field_dict["title"] = title
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if sentences is not UNSET:
            field_dict["sentences"] = sentences
        if categories is not UNSET:
            field_dict["categories"] = categories
        if annotations is not UNSET:
            field_dict["annotations"] = annotations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        text = d.pop("text")

        identifier = d.pop("identifier", UNSET)

        title = d.pop("title", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, AnnotatedDocumentMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = AnnotatedDocumentMetadata.from_dict(_metadata)

        sentences = []
        _sentences = d.pop("sentences", UNSET)
        for sentences_item_data in _sentences or []:
            sentences_item = DocSentence.from_dict(sentences_item_data)

            sentences.append(sentences_item)

        categories = []
        _categories = d.pop("categories", UNSET)
        for categories_item_data in _categories or []:
            categories_item = AnnotatedDocCategory.from_dict(categories_item_data)

            categories.append(categories_item)

        annotations = []
        _annotations = d.pop("annotations", UNSET)
        for annotations_item_data in _annotations or []:
            annotations_item = AnnotatedDocAnnotation.from_dict(annotations_item_data)

            annotations.append(annotations_item)

        annotated_document = cls(
            text=text,
            identifier=identifier,
            title=title,
            metadata=metadata,
            sentences=sentences,
            categories=categories,
            annotations=annotations,
        )

        return annotated_document
