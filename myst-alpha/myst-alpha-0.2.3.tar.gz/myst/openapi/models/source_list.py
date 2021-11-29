from typing import List

from myst.models import base_model

from ..models.source_get import SourceGet


class SourceList(base_model.BaseModel):
    """Schema for source list responses."""

    data: List[SourceGet]
    has_more: bool
