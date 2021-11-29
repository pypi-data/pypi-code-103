from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class ProjectCreate(base_model.BaseModel):
    """Schema for project create requests."""

    object_: Literal["Project"] = Field(..., alias="object")
    title: str
    description: Optional[str] = None
