from typing import List

from myst.models import base_model

from ..models.operation_get import OperationGet


class OperationList(base_model.BaseModel):
    """Schema for operation list responses."""

    data: List[OperationGet]
    has_more: bool
