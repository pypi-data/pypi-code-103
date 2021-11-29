from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class DeploymentCreate(base_model.BaseModel):
    """Schema for deployment create requests."""

    object_: Literal["Deployment"] = Field(..., alias="object")
    title: str
