from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model

from ..models.job_state import JobState


class NodeRunJobGet(base_model.BaseModel):
    """Node run job schema for get responses."""

    object_: Literal["NodeJob"] = Field(..., alias="object")
    uuid: str
    create_time: str
    type: Literal["NodeRunJob"]
    node: str
    start_time: str
    end_time: str
    as_of_time: str
    state: JobState
    update_time: Optional[str] = None
    result: Optional[str] = None
