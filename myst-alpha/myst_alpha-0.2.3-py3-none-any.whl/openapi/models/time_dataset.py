from typing import Any, List, Optional, Union

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model

from ..models.time_dataset_row import TimeDatasetRow


class TimeDataset(base_model.BaseModel):
    """"""

    object_: Literal["TimeDataset"] = Field(..., alias="object")
    cell_shape: List[int]
    sample_period: str
    data: List[TimeDatasetRow]
    coordinate_labels: Optional[List[List[Union[int, str]]]] = None
    axis_labels: Optional[List[Union[int, str]]] = None
    metadata: Optional[Any] = None
