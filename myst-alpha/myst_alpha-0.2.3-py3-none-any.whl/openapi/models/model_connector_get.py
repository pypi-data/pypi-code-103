from typing import Any, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model


class ModelConnectorGet(base_model.BaseModel):
    """Schema for model connector get responses."""

    object_: Literal["Connector"] = Field(..., alias="object")
    type: Literal["ModelConnector"]
    uuid: str
    title: str
    provider: str
    description: str
    parameters_schema: Any
    icon_url: Optional[str] = None
