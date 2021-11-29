from typing import List, Union

from myst.models import base_model

from ..models.model_get import ModelGet
from ..models.operation_get import OperationGet
from ..models.source_get import SourceGet
from ..models.time_series_get import TimeSeriesGet


class ProjectNodesList(base_model.BaseModel):
    """Project nodes list schema."""

    data: List[Union[TimeSeriesGet, SourceGet, OperationGet, ModelGet]]
    has_more: bool
