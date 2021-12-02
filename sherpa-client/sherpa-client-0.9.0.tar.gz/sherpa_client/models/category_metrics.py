from typing import Any, Dict, Type, TypeVar

import attr

from ..models.categories_facets import CategoriesFacets
from ..models.document_facets import DocumentFacets

T = TypeVar("T", bound="CategoryMetrics")


@attr.s(auto_attribs=True)
class CategoryMetrics:
    """ """

    categories_count: int
    categories_facets: CategoriesFacets
    documents_in_dataset: int
    document_facets: DocumentFacets

    def to_dict(self) -> Dict[str, Any]:
        categories_count = self.categories_count
        categories_facets = self.categories_facets.to_dict()

        documents_in_dataset = self.documents_in_dataset
        document_facets = self.document_facets.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "categoriesCount": categories_count,
                "categoriesFacets": categories_facets,
                "documentsInDataset": documents_in_dataset,
                "documentFacets": document_facets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        categories_count = d.pop("categoriesCount")

        categories_facets = CategoriesFacets.from_dict(d.pop("categoriesFacets"))

        documents_in_dataset = d.pop("documentsInDataset")

        document_facets = DocumentFacets.from_dict(d.pop("documentFacets"))

        category_metrics = cls(
            categories_count=categories_count,
            categories_facets=categories_facets,
            documents_in_dataset=documents_in_dataset,
            document_facets=document_facets,
        )

        return category_metrics
