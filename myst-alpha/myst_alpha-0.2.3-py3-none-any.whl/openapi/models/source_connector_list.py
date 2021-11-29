from typing import List

from myst.models import base_model

from ..models.source_connector_get import SourceConnectorGet


class SourceConnectorList(base_model.BaseModel):
    """Schema for source connector list responses."""

    data: List[SourceConnectorGet]
    has_more: bool
