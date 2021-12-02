from typing import Any, Dict, Type, TypeVar

import attr

from ..models.annotation_facets import AnnotationFacets
from ..models.document_facets import DocumentFacets
from ..models.suggestion_facets import SuggestionFacets

T = TypeVar("T", bound="AnnotationMetrics")


@attr.s(auto_attribs=True)
class AnnotationMetrics:
    """ """

    annotation_count: int
    suggestion_count: int
    annotation_facets: AnnotationFacets
    suggestion_facets: SuggestionFacets
    documents_in_dataset: int
    segments_in_dataset: int
    document_facets: DocumentFacets

    def to_dict(self) -> Dict[str, Any]:
        annotation_count = self.annotation_count
        suggestion_count = self.suggestion_count
        annotation_facets = self.annotation_facets.to_dict()

        suggestion_facets = self.suggestion_facets.to_dict()

        documents_in_dataset = self.documents_in_dataset
        segments_in_dataset = self.segments_in_dataset
        document_facets = self.document_facets.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "annotationCount": annotation_count,
                "suggestionCount": suggestion_count,
                "annotationFacets": annotation_facets,
                "suggestionFacets": suggestion_facets,
                "documentsInDataset": documents_in_dataset,
                "segmentsInDataset": segments_in_dataset,
                "documentFacets": document_facets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        annotation_count = d.pop("annotationCount")

        suggestion_count = d.pop("suggestionCount")

        annotation_facets = AnnotationFacets.from_dict(d.pop("annotationFacets"))

        suggestion_facets = SuggestionFacets.from_dict(d.pop("suggestionFacets"))

        documents_in_dataset = d.pop("documentsInDataset")

        segments_in_dataset = d.pop("segmentsInDataset")

        document_facets = DocumentFacets.from_dict(d.pop("documentFacets"))

        annotation_metrics = cls(
            annotation_count=annotation_count,
            suggestion_count=suggestion_count,
            annotation_facets=annotation_facets,
            suggestion_facets=suggestion_facets,
            documents_in_dataset=documents_in_dataset,
            segments_in_dataset=segments_in_dataset,
            document_facets=document_facets,
        )

        return annotation_metrics
