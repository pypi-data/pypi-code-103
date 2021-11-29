from typing import List, Union

from myst.models import base_model

from ..models.model_fit_policy_get import ModelFitPolicyGet
from ..models.time_series_run_policy_get import TimeSeriesRunPolicyGet


class ProjectPoliciesList(base_model.BaseModel):
    """Schema for a list of project policies."""

    data: List[Union[TimeSeriesRunPolicyGet, ModelFitPolicyGet]]
    has_more: bool
