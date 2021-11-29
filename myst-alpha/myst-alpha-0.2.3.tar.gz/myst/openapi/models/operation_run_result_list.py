from typing import List

from myst.models import base_model

from ..models.operation_run_result_get import OperationRunResultGet


class OperationRunResultList(base_model.BaseModel):
    """Schema for operation run result list responses."""

    data: List[OperationRunResultGet]
    has_more: bool
