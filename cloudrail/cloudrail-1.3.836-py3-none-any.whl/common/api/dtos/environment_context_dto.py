from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin

from common.api.dtos.cloud_provider_dto import CloudProviderDTO


@dataclass
class EnvironmentContextResultDTO(DataClassJsonMixin):
    is_success: bool
    context: Optional[str] = None
    error: Optional[str] = None
    drift_track: bool = False
    workspace_id: Optional[str] = None
    cloud_provider: CloudProviderDTO = None
