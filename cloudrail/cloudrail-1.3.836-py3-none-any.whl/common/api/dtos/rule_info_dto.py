from dataclasses import dataclass
from typing import Dict
from typing import List, Optional

from cloudrail.knowledge.rules.rule_metadata import RemediationSteps
from dataclasses_json import DataClassJsonMixin

from common.api.dtos.cloud_provider_dto import CloudProviderDTO
from common.api.dtos.rule_execlusion_dto import RuleExclusionDTO


class RemediationStepsDTO(DataClassJsonMixin, RemediationSteps):
    pass


@dataclass
class RuleInfoDTO(DataClassJsonMixin):
    id: str
    name: str
    description: str
    severity: str
    rule_type: str
    cloud_provider: CloudProviderDTO
    security_layer: str
    resource_types: List[str]
    logic: str
    remediation_steps: RemediationStepsDTO
    active: bool
    associated_policies: List[str]
    rule_exclusion: RuleExclusionDTO
    source_control_link: Optional[str]
    compliance: Dict[str, Dict[str, List[str]]]
    supported_iac_types: List[str]


@dataclass
class RuleUpdateDTO(DataClassJsonMixin):
    active: Optional[bool] = None
    rule_exclusion: Optional[RuleExclusionDTO] = None


@dataclass
class RuleBulkUpdateDTO(DataClassJsonMixin):
    id: str
    active: Optional[bool]
