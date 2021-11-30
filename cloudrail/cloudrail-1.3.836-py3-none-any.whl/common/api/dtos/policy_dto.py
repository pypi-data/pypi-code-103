from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin

from common.input_validator import InputValidator


class RuleEnforcementModeDTO(str, Enum):
    ADVISE = 'advise'
    MANDATE_ALL_RESOURCES = 'mandate'
    MANDATE_NEW_RESOURCES = 'mandate_new_resources'
    IGNORE = 'ignore'

    @property
    def is_mandate(self):
        return self in (RuleEnforcementModeDTO.MANDATE_NEW_RESOURCES, RuleEnforcementModeDTO.MANDATE_ALL_RESOURCES)


@dataclass
class PolicyRuleDTO(DataClassJsonMixin):
    rule_id: str
    enforcement_mode: RuleEnforcementModeDTO

    def __post_init__(self):
        InputValidator.validate_allowed_chars(self.rule_id)


@dataclass
class PolicyRuleBulkAddDataDTO(DataClassJsonMixin):
    id: str
    policy_rules: List[PolicyRuleDTO]

    def __post_init__(self):
        InputValidator.validate_uuid(self.id)


@dataclass
class PolicyAddDTO(DataClassJsonMixin):
    """
    ---
    properties:
        name:
            type: string
            description: 
                The name of the policy (displayed to the user).
        description:
            type: string
            description: 
                The user-provided description for the policy.
        active:
            type: boolean
            description:
                Set to "true" if the policy is currently active.
    """
    name: str
    description: str
    policy_rules: List[PolicyRuleDTO] = field(default_factory=list)
    account_config_ids: List[str] = field(default_factory=list)
    active: bool = True

    def __post_init__(self):
        InputValidator.validate_allowed_chars(self.name)
        InputValidator.validate_allowed_chars(self.description)
        for account_config_id in self.account_config_ids:
            InputValidator.validate_uuid(account_config_id)


@dataclass
class PolicyDTO(DataClassJsonMixin):
    """
    ---
    properties:
        name:
            type: string
            description:
                The name of the policy (displayed to the user).
        description:
            type: string
            description:
                The user-provided description for the policy.
        account_config_ids:
            type: string
            description:
                A list of accounts the policy is applied to, identified by their account config IDs.
        id:
            type: string
            description:
                The unique identifier of the policy in the Cloudrail system.
        created_at:
            type: string
            description:
                The date when the policy was first created.
        updated_at:
            type: string
            description:
                The date when the policy was last updated.
        active:
            type: boolean
            description:
                Set to "true" if the policy is currently active.
        is_deleted:
            type: boolean
            description:
                Set to "true" if the policy has been deleted. We do not
                remove policies from the database entirely to maintain
                historical data.
    """
    name: str
    description: str
    policy_rules: List[PolicyRuleDTO] = field(default_factory=list)
    account_config_ids: List[str] = field(default_factory=list)
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    active: bool = True
    is_deleted: bool = False


@dataclass
class PolicyUpdateDTO(DataClassJsonMixin):
    """
    ---
    properties:
        name:
            type: string
            description:
                The name of the policy (displayed to the user).
        description:
            type: string
            description:
                The user-provided description for the policy.
        active:
            type: boolean
            description:
                Set to "true" if the policy is currently active.
        account_config_ids:
            type: string
            description:
                A list of accounts the policy is applied to, identified by their account config IDs.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    account_config_ids: Optional[List[str]] = None

    def __post_init__(self):
        InputValidator.validate_allowed_chars(self.name, True)
        InputValidator.validate_allowed_chars(self.description, True)
        if self.account_config_ids:
            for account_config_id in self.account_config_ids:
                InputValidator.validate_uuid(account_config_id)



@dataclass
class PolicyRuleUpdateDTO(DataClassJsonMixin):
    enforcement_mode: RuleEnforcementModeDTO
