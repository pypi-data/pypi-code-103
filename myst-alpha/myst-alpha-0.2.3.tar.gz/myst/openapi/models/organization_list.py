from typing import List

from myst.models import base_model

from ..models.organization_get import OrganizationGet


class OrganizationList(base_model.BaseModel):
    """Schema for organization list responses."""

    data: List[OrganizationGet]
    has_more: bool
