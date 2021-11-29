from typing import Any, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class SourceCreate(base_model.BaseModel):
    """Schema for source create requests."""

    title: str
    project: str
    connector_uuid: str
    object_: Optional[Literal["Node"]] = Field("Node", alias="object")
    type: Optional[Literal["Source"]] = "Source"
    description: Optional[str] = None
    parameters: Optional[Any] = None
