from typing import Any, Dict, Type, TypeVar

import attr

from ..models.document_facets import DocumentFacets

T = TypeVar("T", bound="CorpusMetrics")


@attr.s(auto_attribs=True)
class CorpusMetrics:
    """ """

    document_count: int
    segment_count: int
    corpus_size: int
    document_facets: DocumentFacets

    def to_dict(self) -> Dict[str, Any]:
        document_count = self.document_count
        segment_count = self.segment_count
        corpus_size = self.corpus_size
        document_facets = self.document_facets.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "documentCount": document_count,
                "segmentCount": segment_count,
                "corpusSize": corpus_size,
                "documentFacets": document_facets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        document_count = d.pop("documentCount")

        segment_count = d.pop("segmentCount")

        corpus_size = d.pop("corpusSize")

        document_facets = DocumentFacets.from_dict(d.pop("documentFacets"))

        corpus_metrics = cls(
            document_count=document_count,
            segment_count=segment_count,
            corpus_size=corpus_size,
            document_facets=document_facets,
        )

        return corpus_metrics
