from typing import List

from myst.models import base_model

from ..models.operation_connector_get import OperationConnectorGet


class OperationConnectorList(base_model.BaseModel):
    """Schema for operation connector list responses."""

    data: List[OperationConnectorGet]
    has_more: bool
