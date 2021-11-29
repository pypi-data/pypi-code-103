from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class ModelFitResultGetDetailed(base_model.BaseModel):
    """Schema for model fit result get responses."""

    object_: Literal["NodeResult"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["ModelFitResult"]
    node: str
    start_time: str
    end_time: str
    as_of_time: str
    fit_state_url: str
    update_time: Optional[str] = None
