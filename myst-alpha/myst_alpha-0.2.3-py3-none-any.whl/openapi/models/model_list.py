from typing import List

from myst.models import base_model

from ..models.model_get import ModelGet


class ModelList(base_model.BaseModel):
    """Schema for model list responses."""

    data: List[ModelGet]
    has_more: bool
