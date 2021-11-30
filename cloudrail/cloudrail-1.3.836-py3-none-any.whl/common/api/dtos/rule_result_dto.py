from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from cloudrail.knowledge.context.iac_type import IacType
from dataclasses_json import DataClassJsonMixin

from common.api.dtos.cloud_provider_dto import CloudProviderDTO
from common.api.dtos.datetime_field import datetime_field
from common.api.dtos.policy_dto import RuleEnforcementModeDTO


class IssueSeverityDTO(str, Enum):
    WARNING = 'warning'


class RuleResultStatusDTO(str, Enum):
    SUCCESS = 'success'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    IGNORED = 'ignored'


@dataclass
class IacResourceMetadataDTO(DataClassJsonMixin):
    iac_entity_id: str
    file_name: str
    start_line: int
    end_line: int
    module_metadata: Optional['IacResourceMetadataDTO'] = None
    id: Optional[str] = None


@dataclass
class ContextEntityDTO(DataClassJsonMixin):
    id: str
    name: Optional[str]
    cloud_entity_id: Optional[str]
    type: str
    is_pseudo: bool
    managed_by_iac: Optional[bool] = None
    iac_entity_id: Optional[str] = None
    cloud_resource_url: Optional[str] = None
    iac_resource_metadata: Optional[IacResourceMetadataDTO] = None
    created_at: datetime = datetime_field()
    friendly_name: str = None
    iac_resource_url: Optional[str] = None

    def get_friendly_name(self) -> str:
        return self.iac_entity_id or self.name or self.cloud_entity_id


@dataclass
class IssueItemDTO(DataClassJsonMixin):
    evidence: str
    exposed_entity: Optional[ContextEntityDTO] = None
    violating_entity: Optional[ContextEntityDTO] = None


@dataclass
class RuleResultDTO(DataClassJsonMixin):
    # Rule result data:
    id: str
    status: RuleResultStatusDTO
    issue_items: List[IssueItemDTO]
    enforcement_mode: RuleEnforcementModeDTO
    created_at: str
    # rule meta data
    rule_id: Optional[str] = None
    rule_name: Optional[str] = None
    rule_description: Optional[str] = None
    rule_logic: Optional[str] = None
    severity: Optional[str] = None
    rule_type: Optional[str] = None
    security_layer: Optional[str] = None
    resource_types: Optional[List[str]] = None
    compliance: Optional[Dict[str, Dict[str, List[str]]]] = None
    iac_remediation_steps: Optional[str] = None
    console_remediation_steps: Optional[str] = None
    source_control_link: Optional[str] = None
    # account
    account_config_id: Optional[str] = None
    # assessment data
    assessment_id: Optional[str] = None
    # policy data
    policy_id: Optional[str] = None
    is_custom: bool = False
    cloud_provider: Optional[CloudProviderDTO] = None
    iac_type: Optional[IacType] = None

    @property
    def is_mandate(self):
        return self.enforcement_mode.is_mandate


@dataclass
class AccountRuleResultStatusDTO(DataClassJsonMixin):
    customer_id: str = None
    account_config_id: str = None
    rule_id: str = None
    status: RuleResultStatusDTO = None
    cspm_assessment_job_id: str = None
    created_at: str = None
    updated_at: str = None
