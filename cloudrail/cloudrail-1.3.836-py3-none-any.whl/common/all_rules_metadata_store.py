from typing import List, Set, Optional

from cloudrail.knowledge.context.cloud_provider import CloudProvider
from cloudrail.knowledge.rules.rule_metadata import RuleMetadata, rule_matches_query, RemediationSteps
from cloudrail.knowledge.rules.rules_metadata_store import CloudrailRulesMetadataStore, RulesMetadataStore

from cloudrail.knowledge.context.iac_type import IacType 
from common.exceptions import NotFoundException
from common.rule_metadata.checkov_rules_metadata_store import CheckovRulesMetadataStore

RULE_ID = 'rule_id'
NAME = 'name'
DESCRIPTION = 'description'
LOGIC = 'human_readable_logic'
CONSOLE_REMEDIATION_STEPS = 'console_remediation_steps'
IAC_REMEDIATION_STEPS = 'iac_remediation_steps'
SEVERITY = 'severity'
RULE_TYPE = 'rule_type'
SECURITY_LAYER = 'security_layer'
RESOURCE_TYPE = 'resource_type'
CLOUD_PROVIDER = 'cloud_provider'
RULE_METADATA_NOT_FOUND = 'Rule {} metadata not found'


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AllRulesMetadataStore(RulesMetadataStore, metaclass=Singleton):
    def __init__(self):
        super().__init__({})
        cloudrail_metadata = CloudrailRulesMetadataStore().rules_metadata
        checkov_metadata = CheckovRulesMetadataStore().rules_metadata
        self.rules_metadata = {**cloudrail_metadata, **checkov_metadata}

    def list_rules_ids(self, provider: CloudProvider = None) -> Set[str]:
        if provider:
            return {metadata.rule_id for metadata in self.list_rules_metadata() if metadata.cloud_provider == provider}
        else:
            return set(self.rules_metadata.keys())

    def list_checkov_rule_ids(self, cloud_provider: Optional[CloudProvider] = None) -> List[str]:
        checkov_rules = [rule for rule in self.list_rules_metadata() if rule.rule_id.startswith('CKV_') and not rule.is_deleted]
        return [rule.rule_id for rule in checkov_rules if not cloud_provider or rule.cloud_provider == cloud_provider]

    def get_by_rule_id(self, rule_id: str) -> RuleMetadata:
        rule_metadata = self.rules_metadata.get(rule_id)
        if not rule_metadata:
            raise NotFoundException(RULE_METADATA_NOT_FOUND.format(rule_id))
        return rule_metadata

    def query_rules_metadata(self, text: Optional[str] = None,
                             iac_type: IacType = None) -> List[RuleMetadata]:

        rules_metadata: List[RuleMetadata]
        if iac_type:
            rules_metadata = [metadata for metadata in self.list_rules_metadata()
                              if iac_type in metadata.supported_iac_types]
        else:
            rules_metadata = self.list_rules_metadata()

        if not text:
            return rules_metadata
        rules = []
        for rule in rules_metadata:
            if rule_matches_query(rule.rule_id, rule.name, text):
                rules.append(rule)
        return rules


AllRulesMetadataStoreInstance = AllRulesMetadataStore()


def get_remediation_steps_by_iac_type(remediation_steps: RemediationSteps, iac_type: IacType) -> str:
    iac_remediation_steps: str = ''
    if iac_type == IacType.TERRAFORM:
        iac_remediation_steps = remediation_steps.terraform
    elif iac_type == IacType.CLOUDFORMATION:
        iac_remediation_steps = remediation_steps.cloudformation
    return iac_remediation_steps
