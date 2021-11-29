from typing import List, Union

from myst.models import base_model

from ..models.model_fit_result_get import ModelFitResultGet
from ..models.model_run_result_get import ModelRunResultGet
from ..models.operation_run_result_get import OperationRunResultGet
from ..models.source_run_result_get import SourceRunResultGet
from ..models.time_series_insert_result_get import TimeSeriesInsertResultGet
from ..models.time_series_run_result_get import TimeSeriesRunResultGet


class ProjectResultList(base_model.BaseModel):
    """Project result list schema."""

    data: List[
        Union[
            SourceRunResultGet,
            ModelRunResultGet,
            OperationRunResultGet,
            TimeSeriesRunResultGet,
            TimeSeriesInsertResultGet,
            ModelFitResultGet,
        ]
    ]
    has_more: bool
