from typing import List, Tuple

from cloudrail.knowledge.context.iac_type import IacType
from cloudrail.knowledge.utils.string_utils import StringUtils
from cloudrail.cli.result_formatter.base_formatter import BaseFormatter
from common.api.dtos.assessment_job_dto import IacAssessmentJobDTO
from common.api.dtos.policy_dto import PolicyDTO
from common.api.dtos.rule_result_dto import RuleResultDTO, RuleResultStatusDTO
from colorama import Fore, Style


class TextFormatter(BaseFormatter):
    def __init__(self, stylize: bool, show_warnings: bool, show_warnings_descriptions: bool):
        super().__init__()
        if stylize:
            self._error_rule_name_style = Fore.RED + Style.BRIGHT
            self._warning_rule_name_style = Fore.YELLOW + Style.BRIGHT
            self._rule_description_style = Fore.CYAN
            self._resource_style = Fore.BLUE
            self._resource_type_style = Fore.MAGENTA
            self._evidence_style = Fore.CYAN
            self._reset_style = Style.RESET_ALL
            self._pseudo_style = Fore.YELLOW
            self._no_policy_style = Fore.YELLOW
            self._unknown_block_style = Fore.YELLOW
            self._invalidation_info_style = Fore.YELLOW
        self._show_warnings = show_warnings
        self._show_warnings_descriptions = show_warnings_descriptions

    def format(self, rule_results: List[RuleResultDTO],
               run_exec: IacAssessmentJobDTO,
               policies: List[PolicyDTO]) -> Tuple[str, str]:
        show_pseudo_message = False
        show_no_policy_message = False
        warnings: List[RuleResultDTO] = []
        failures: List[RuleResultDTO] = []
        success: List[RuleResultDTO] = []
        number_of_ignored_rules = 0
        number_of_skipped_rules = 0

        for rule_result in rule_results:
            if rule_result.status == RuleResultStatusDTO.FAILED:
                if rule_result.is_mandate:
                    failures.append(rule_result)
                else:
                    warnings.append(rule_result)
            elif rule_result.status == RuleResultStatusDTO.SUCCESS:
                success.append(rule_result)
            elif rule_result.status == RuleResultStatusDTO.SKIPPED:
                number_of_skipped_rules += 1
            elif rule_result.status == RuleResultStatusDTO.IGNORED:
                number_of_ignored_rules += 1

        format_result = [self._reset_style]
        if len(failures) > 0:
            format_result.append('ERRORs found:')
            format_result.extend(self._get_failed_rule_result_text(failures, True, self._error_rule_name_style))
            show_pseudo_message = self._has_issue_items_with_pseudo_data(rule_results)

        if len(warnings) > 0 and self._show_warnings:
            format_result.append('WARNINGs found:')
            format_result.extend(self._get_failed_rule_result_text(warnings,
                                                                   self._show_warnings_descriptions,
                                                                   self._warning_rule_name_style))
            show_pseudo_message = show_pseudo_message or self._has_issue_items_with_pseudo_data(rule_results)
            show_no_policy_message = len(policies) == 0

        if show_pseudo_message:
            format_result.extend(self._pseudo_message)

        if show_no_policy_message:
            format_result.extend(self._no_policy_message)

        notices = self._get_unknown_block_message(run_exec.tf_unknown_blocks)
        notices.extend(self._get_invalidation_message(run_exec.invalidation_info, self._show_warnings))

        notices.append('')
        notices.append('Summary:')
        notices.append('{0} Rules Violated:'.format(len(warnings) + len(failures)))
        notices.append(Fore.RED + '  {0} Mandated Rules (these are considered FAILURES)'.format(len(failures)))
        notices.append(Fore.YELLOW + '  {0} Advisory Rules (these are considered WARNINGS)'.format(len(warnings)))
        notices.append(Fore.BLUE + '{0} Ignored Rules'.format(number_of_ignored_rules))
        notices.append(Fore.BLUE + '{0} Rules Skipped (no relevant resources found)'.format(number_of_skipped_rules))
        notices.append(Fore.GREEN + '{0} Rules Passed'.format(len(success)))
        notices.append('')

        if not self._show_warnings and len(warnings) > 0:
            notices.append(Fore.WHITE + Style.BRIGHT + 'NOTE: WARNINGs are not listed by default. Please use the "-v" option to list them.')
            notices.append('')

        return f'{self._reset_style}\n'.join(format_result), '\n'.join(notices)

    def _get_failed_rule_result_text(self,
                                     rule_results: List[RuleResultDTO],
                                     show_description: bool,
                                     rule_name_style: str) -> List[str]:
        format_result = []
        for rule_result in rule_results:
            format_result.append(f'{rule_name_style}Rule: {rule_result.rule_name}')
            if show_description:
                format_result.append(f'{self._rule_description_style}Description: {rule_result.rule_description}')

            format_result.append(f'{self._rule_description_style}Remediation Steps - Cloud Console: '
                                 f'{StringUtils.clean_markdown(rule_result.console_remediation_steps)}')

            iac_type: str = IacType.to_string(rule_result.iac_type)
            format_result.append(f'{self._rule_description_style}Remediation Steps - {iac_type}: '
                                 f'{StringUtils.clean_markdown(rule_result.iac_remediation_steps)}')
            format_result.append(f' - {len(rule_result.issue_items)} Resources Exposed:')
            format_result.append('-----------------------------------------------')

            for item in rule_result.issue_items:
                item_msg = self._format_issue_item(item)
                format_result.extend(item_msg)
                format_result.append('')
            format_result.append('-----------------------------------------------')
        return format_result

    def _has_issue_items_with_pseudo_data(self, rule_results: List[RuleResultDTO]) -> bool:
        return any(self._issue_item_contains_pseudo_entity(issue_item) for rule_result in rule_results
                   if rule_result.status == RuleResultStatusDTO.FAILED for issue_item in rule_result.issue_items)
