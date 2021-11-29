from typing import List

from myst.models import base_model

from ..models.time_dataset_spec import TimeDatasetSpec


class OutputSpecsGet(base_model.BaseModel):
    """Schema for node output spec responses."""

    output_specs: List[TimeDatasetSpec]
