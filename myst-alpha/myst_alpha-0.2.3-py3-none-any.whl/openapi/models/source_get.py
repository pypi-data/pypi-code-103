from typing import Any, List, Optional

from pydantic import Field
from typing_extensions import Literal

from myst.models import base_model

from ..models.deploy_status import DeployStatus
from ..models.time_dataset_spec import TimeDatasetSpec


class SourceGet(base_model.BaseModel):
    """Schema for source get responses."""

    object_: Literal["Node"] = Field(..., alias="object")
    uuid: str
    create_time: str
    organization: str
    owner: str
    type: Literal["Source"]
    title: str
    project: str
    creator: str
    deploy_status: DeployStatus
    connector_uuid: str
    parameters: Any
    update_time: Optional[str] = None
    description: Optional[str] = None
    output_specs: Optional[List[TimeDatasetSpec]] = None
