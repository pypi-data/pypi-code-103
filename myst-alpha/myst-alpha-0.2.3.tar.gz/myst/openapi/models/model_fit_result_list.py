from typing import List

from myst.models import base_model

from ..models.model_fit_result_get import ModelFitResultGet


class ModelFitResultList(base_model.BaseModel):
    """Schema for model fit result list responses."""

    data: List[ModelFitResultGet]
    has_more: bool
