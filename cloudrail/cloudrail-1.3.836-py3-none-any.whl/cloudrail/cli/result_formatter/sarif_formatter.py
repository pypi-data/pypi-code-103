import json
from typing import Tuple, List


from common.api.dtos.policy_dto import RuleEnforcementModeDTO, PolicyDTO
from common.api.dtos.rule_result_dto import RuleResultDTO, ContextEntityDTO, RuleResultStatusDTO
from common.api.dtos.assessment_job_dto import IacAssessmentJobDTO
from cloudrail.knowledge.rules.rule_metadata import RuleType
from cloudrail.knowledge.context.iac_type import IacType
from cloudrail.knowledge.utils.string_utils import StringUtils
from cloudrail.cli.result_formatter.base_formatter import BaseFormatter


class SarifFormatter(BaseFormatter):

    def __init__(self, show_warnings: bool):
        super().__init__()
        self._show_warnings = show_warnings

    def format(self,
               rule_results: List[RuleResultDTO],
               unused_run_exec: IacAssessmentJobDTO,
               unused_policies: List[PolicyDTO]) -> Tuple[str, str]:
        filtered_results = []
        for rule_result in rule_results:
            if rule_result.status == RuleResultStatusDTO.FAILED and \
                    (rule_result.is_mandate or self._show_warnings):
                filtered_results.append(rule_result)

        result = {
            'version': '2.1.0',
            '$schema': 'https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.4.json',
            'runs': [
                {
                    'tool': {
                        'driver': {
                            'name': 'Indeni Cloudrail',
                            'rules': self._convert_rules_info(filtered_results)
                        }
                    },
                    "results": self._convert_issue_items_to_sarif_results(filtered_results)
                }],
        }
        return json.dumps(result), ''

    @classmethod
    def _convert_rules_info(cls, rule_results: List[RuleResultDTO]):
        rules_info = []
        for rule_result in rule_results:
            text: str = f'Remediation Steps - Cloud Console: {StringUtils.clean_markdown(rule_result.console_remediation_steps)}'
            iac_type: str = IacType.to_string(rule_result.iac_type)
            text += f'\nRemediation Steps - {iac_type}: {StringUtils.clean_markdown(rule_result.iac_remediation_steps)}'
            rules_info.append({
                'id': rule_result.rule_id,
                'name': rule_result.rule_name,
                'shortDescription': {'text': rule_result.rule_name},
                'fullDescription': {'text': rule_result.rule_description},
                'help': {'text': text},
                'properties': {'precision': cls._get_rule_precision(rule_result)}
            })
        return rules_info

    @staticmethod
    def _get_rule_precision(rule_result: RuleResultDTO):
        if RuleType.CONTEXT_AWARE == rule_result.rule_type:
            return 'very-high'
        else:
            return 'medium'

    @classmethod
    def _convert_issue_items_to_sarif_results(cls, rule_results: List[RuleResultDTO]):
        vulns = []
        for rule_result in rule_results:
            for issue_item in rule_result.issue_items:
                violating_entity = issue_item.violating_entity
                exposed_entity = issue_item.exposed_entity
                location = cls._get_location(violating_entity, exposed_entity)
                if location:
                    vulns.append({
                        "ruleId": rule_result.rule_id,
                        "level": cls._get_level(rule_result.enforcement_mode),
                        "message": {
                            "text": '<{}> is exposing <{}>'.format(violating_entity.get_friendly_name(),
                                                                   exposed_entity.get_friendly_name()),
                            "markdown": '<`{}`> is exposing <`{}`>'.format(violating_entity.get_friendly_name(),
                                                                           exposed_entity.get_friendly_name())
                        },
                        "locations": [cls._get_location(violating_entity, exposed_entity)]
                    })
        return vulns

    @staticmethod
    def _get_location(violating_entity: ContextEntityDTO, exposed_entity: ContextEntityDTO):
        iac_resource_metadata = violating_entity.iac_resource_metadata or exposed_entity.iac_resource_metadata
        if iac_resource_metadata:
            return {
                'physicalLocation': {
                    'artifactLocation': {
                        'uri': iac_resource_metadata.file_name
                    },
                    'region': {
                        'startLine': iac_resource_metadata.start_line,
                        'endLine': iac_resource_metadata.end_line
                    }
                }
            }
        return None

    @staticmethod
    def _get_level(enforcement_mode: RuleEnforcementModeDTO) -> str:
        if enforcement_mode.is_mandate:
            return 'error'
        return 'warning'
