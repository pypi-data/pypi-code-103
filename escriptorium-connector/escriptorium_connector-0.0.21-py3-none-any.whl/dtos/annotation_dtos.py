from enum import Enum
from typing import List, Union, Any
from dataclasses import dataclass

from .super_dtos import PagenatedResponse


class TextMarkerType(str, Enum):
    BACKGROUNDCOLOR = "Background Color"
    TEXTCOLOR = "Text Color"
    BOLD = "Bold"
    ITALIC = "Italic"


@dataclass(init=True, frozen=True)
class PostTypology:
    name: str


@dataclass(init=True, frozen=True)
class GetTypology:
    pk: int
    name: str


@dataclass(init=True, frozen=True)
class PostComponent:
    name: str
    allowed_values: List[str]


@dataclass(init=True, frozen=True)
class GetComponent:
    pk: int
    name: str
    allowed_values: List[str]


@dataclass(init=True, frozen=True)
class PostAnnotationTaxonomy:
    document: int
    name: str
    marker_type: TextMarkerType
    marker_detail: str
    has_comments: bool
    typology: PostTypology
    components: List[PostComponent]


@dataclass(init=True, frozen=True)
class GetAnnotationTaxonomy:
    pk: int
    document: int
    name: str
    marker_type: TextMarkerType
    marker_detail: str
    has_comments: bool
    typology: GetTypology
    components: List[GetComponent]


class GetAnnotationTaxonomies(PagenatedResponse):
    results: List[GetAnnotationTaxonomy]

    def __init__(
        self,
        count: int,
        next: Union[str, None],
        previous: Union[str, None],
        results: List[Any] = [],
    ):
        super(GetAnnotationTaxonomies, self).__init__(count, next, previous)
        self.results = [GetAnnotationTaxonomy(**x) for x in results]
