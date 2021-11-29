from typing import List

from myst.models import base_model

from ..models.model_connector_get import ModelConnectorGet


class ModelConnectorList(base_model.BaseModel):
    """Schema for model connector list responses."""

    data: List[ModelConnectorGet]
    has_more: bool
