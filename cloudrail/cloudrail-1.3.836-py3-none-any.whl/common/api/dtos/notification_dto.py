from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from cloudrail.knowledge.rules.rule_metadata import RuleSeverity
from dataclasses_json import DataClassJsonMixin

from common.api.dtos.policy_dto import RuleEnforcementModeDTO
from common.input_validator import InputValidator


class EventType(str, Enum):
    NEW_DRIFT_DETECTED = 'new_drift_detected'
    NEW_IAC_VIOLATION = 'new_iac_violation'
    NEW_SCPM_VIOLATION = 'new_cspm_violation'


@dataclass
class AddUpdateNotificationConfigDTO(DataClassJsonMixin):
    name: Optional[str] = None
    event_type: Optional[EventType] = None
    targets: Optional[dict] = None
    enabled: Optional[bool] = None
    enforcement_modes: List[RuleEnforcementModeDTO] = field(default_factory=list)
    severities: List[RuleSeverity] = field(default_factory=list)
    account_config_ids: List[str] = field(default_factory=list)

    def __post_init__(self):
        for account_config_id in self.account_config_ids:
            InputValidator.validate_uuid(account_config_id)


@dataclass
class NotificationTargetsDTO(DataClassJsonMixin):
    webhook: str = None
    emails: List[str] = field(default_factory=list)


@dataclass
class NotificationConfigDTO(DataClassJsonMixin):
    id: str
    name: str
    enabled: bool
    event_type: EventType
    targets: NotificationTargetsDTO
    created_at: str
    updated_at: str
    account_config_ids: List[str] = field(default_factory=list)
    enforcement_modes: List[RuleEnforcementModeDTO] = field(default_factory=list)
    severities: List[str] = field(default_factory=list)
