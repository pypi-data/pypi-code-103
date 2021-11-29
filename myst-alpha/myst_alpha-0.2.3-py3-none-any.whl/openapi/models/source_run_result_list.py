from typing import List

from myst.models import base_model

from ..models.source_run_result_get import SourceRunResultGet


class SourceRunResultList(base_model.BaseModel):
    """Schema for source run result list responses."""

    data: List[SourceRunResultGet]
    has_more: bool
