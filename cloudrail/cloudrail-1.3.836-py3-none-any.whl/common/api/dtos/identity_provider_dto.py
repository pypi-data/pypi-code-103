from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin

# pylint:disable=invalid-name
from common.api.dtos.user_dto import RoleTypeDTO


@dataclass
class IdentityProviderDTO(DataClassJsonMixin):
    provider_name: str
    provider_type: str


@dataclass
class ExtendedIdentityProviderDTO(IdentityProviderDTO):
    customer_id: str
    default_permissions: RoleTypeDTO
    created_at: str
    updated_at: str


@dataclass
class SSOSettingsDTO(DataClassJsonMixin):
    saml_metadata_file: Optional[str] = None
    default_permissions: Optional[RoleTypeDTO] = None
