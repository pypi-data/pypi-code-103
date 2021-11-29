from typing import List

from myst.models import base_model

from ..models.model_run_result_get import ModelRunResultGet


class ModelRunResultList(base_model.BaseModel):
    """Schema for model run result list responses."""

    data: List[ModelRunResultGet]
    has_more: bool
