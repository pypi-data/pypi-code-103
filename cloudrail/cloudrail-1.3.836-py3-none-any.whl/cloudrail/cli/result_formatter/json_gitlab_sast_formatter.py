import json
from typing import Tuple, List


from common.api.dtos.policy_dto import PolicyDTO
from common.api.dtos.rule_result_dto import RuleResultDTO, ContextEntityDTO, RuleResultStatusDTO
from common.api.dtos.assessment_job_dto import IacAssessmentJobDTO
from common.utils.datetime_utils import convert_datetime_to_str
from cloudrail.knowledge.rules.rule_metadata import RuleSeverity
from cloudrail.cli.result_formatter.base_formatter import BaseFormatter
from cloudrail.cli import _version


class JsonGitLabSastFormatter(BaseFormatter):
    def __init__(self, show_warnings: bool):
        super().__init__()
        self._show_warnings = show_warnings

    def format(self, rule_results: List[RuleResultDTO],
               run_exec: IacAssessmentJobDTO,
               unused_policies: List[PolicyDTO]) -> Tuple[str, str]:
        filtered_results = []
        for rule_result in rule_results:
            if rule_result.status == RuleResultStatusDTO.FAILED and \
                    (rule_result.is_mandate or self._show_warnings):
                filtered_results.append(rule_result)
        result = {
            "version": "2.0",
            "vulnerabilities": self.convert_issue_items_to_githab_vulns(filtered_results),
            "scan": self._get_scanner(run_exec)
        }
        return json.dumps(result), ''

    @staticmethod
    def convert_issue_items_to_githab_vulns(rule_results: List[RuleResultDTO]):
        vulns = []
        for rule_result in rule_results:
            for issue_item in rule_result.issue_items:
                violating_entity = issue_item.violating_entity
                exposed_entity = issue_item.exposed_entity
                location = JsonGitLabSastFormatter._get_location(violating_entity, exposed_entity)
                if location:
                    vulns.append({
                        "id": rule_result.id + violating_entity.id + exposed_entity.id,
                        "category": "sast",
                        "name": rule_result.rule_name,
                        "message": rule_result.rule_name + ": <" + violating_entity.get_friendly_name()
                                   + "> is exposing <" + exposed_entity.get_friendly_name() + ">",
                        "description": rule_result.rule_description,
                        "severity": JsonGitLabSastFormatter._get_severity(rule_result.severity),
                        "confidence": "High",
                        "scanner": {
                            "id": "indeni_cloudrail",
                            "name": "Indeni Cloudrail"
                        },
                        "location": location
                    })
        return vulns

    @staticmethod
    def _get_location(violating_entity: ContextEntityDTO, exposed_entity: ContextEntityDTO):
        iac_resource_metadata = violating_entity.iac_resource_metadata or exposed_entity.iac_resource_metadata
        if iac_resource_metadata:
            return {
                "file": iac_resource_metadata.file_name,
                "start_line": iac_resource_metadata.start_line,
                "end_line": iac_resource_metadata.end_line
            }
        return None

    @staticmethod
    def _get_severity(severity_dto: str) -> str:
        if severity_dto == RuleSeverity.MAJOR:
            return 'High'
        return severity_dto.title()

    @staticmethod
    def _get_scanner(run_exec: IacAssessmentJobDTO) -> dict:
        datetime_format = '%Y-%m-%d %H:%M'
        return {
            "scanner": {
                "id": "indeni_cloudrail",
                "name": "Cloudrail",
                "vendor": {
                    "name": "Indeni"
                },
                "version": _version.__version__
            },
            "start_time": convert_datetime_to_str(run_exec.created_at, datetime_format),
            "end_time": convert_datetime_to_str(run_exec.ended_at, datetime_format),
            "status": "success",
            "messages": [
            ],
            "type": "sast"
        }
