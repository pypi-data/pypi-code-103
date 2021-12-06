from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.metadata_count import MetadataCount

T = TypeVar("T", bound="DocumentFacets")


@attr.s(auto_attribs=True)
class DocumentFacets:
    """ """

    metadata: str
    facets: List[MetadataCount]

    def to_dict(self) -> Dict[str, Any]:
        metadata = self.metadata
        facets = []
        for facets_item_data in self.facets:
            facets_item = facets_item_data.to_dict()

            facets.append(facets_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "metadata": metadata,
                "facets": facets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        metadata = d.pop("metadata")

        facets = []
        _facets = d.pop("facets")
        for facets_item_data in _facets:
            facets_item = MetadataCount.from_dict(facets_item_data)

            facets.append(facets_item)

        document_facets = cls(
            metadata=metadata,
            facets=facets,
        )

        return document_facets
