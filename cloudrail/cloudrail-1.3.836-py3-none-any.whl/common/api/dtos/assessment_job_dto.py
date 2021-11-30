from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from cloudrail.knowledge.context.iac_type import IacType
from dataclasses_json import DataClassJsonMixin

from common.api.dtos.datetime_field import datetime_field


class AssessmentResultTypeDTO(str, Enum):
    PASSED = 'passed'
    PASSED_WITH_WARNINGS = 'passed_with_warnings'
    FAILED_DUE_TO_VIOLATIONS = 'failed_due_to_violations'


class RunOriginDTO(str, Enum):
    WORKSTATION = 'workstation'
    CI = 'ci'
    TERRAFORM_CLOUD = 'terraform_cloud'


class RunStatusDTO(str, Enum):
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'
    PENDING = 'pending'


class AssessmentStepDTO(str, Enum):
    COLLECT = 'collect'
    WAIT_FOR_CONTEXT = 'wait_for_context'
    WAIT_FOR_COLLECT = 'wait_for_collect'
    PROCESS_STARTED = 'process_started'
    PROCESS_RUNNING_TF_SHOW = 'process_running_tf_show'
    PROCESS_BUILDING_ENV_CONTEXT = 'process_building_env_context'
    RUN_RULES = 'run_rules'
    RUN_CUSTOM_RULES = 'run_custom_rules'
    SAVING_RESULTS = 'saving_results'
    UNKNOWN = 'unknown'


class RunTypeDTO(str, Enum):
    COLLECT = 'collect'
    COLLECT_PROCESS_TEST = 'collect_process_test'
    PROCESS_TEST = 'process_test'


class BlockTypeDTO(str, Enum):
    DATASOURCE = 'datasource'


@dataclass
class UnknownBlockDTO:
    block_type: BlockTypeDTO
    block_address: str


@dataclass
class ManagedResourcesSummaryDTO(DataClassJsonMixin):
    created: int = 0
    updated: int = 0
    deleted: int = 0
    total: int = 0


@dataclass
class InvalidationInfoDTO(DataClassJsonMixin):
    invalidated_resource_id: str
    invalidation_reason: str


@dataclass
class ResultsSummaryDTO(DataClassJsonMixin):
    assessment_result_type: AssessmentResultTypeDTO = AssessmentResultTypeDTO.PASSED
    evaluated_rules: int = 0
    passed_rules: int = 0
    failed_rules: int = 0
    skipped_rules: int = 0
    ignored_rules: int = 0
    failed_mandate: int = 0
    failed_advise: int = 0


@dataclass
class IacAssessmentJobDTO(DataClassJsonMixin):
    id: str
    account_config_id: str
    customer_id: str
    run_status: RunStatusDTO
    run_type: RunTypeDTO = None
    last_step: Optional[AssessmentStepDTO] = None
    error_message: Optional[str] = None
    created_at: datetime = datetime_field()
    ended_at: Optional[datetime] = None
    tf_unknown_blocks: List[UnknownBlockDTO] = field(default_factory=list)
    origin: Optional[RunOriginDTO] = None
    build_link: Optional[str] = None
    execution_source_identifier: Optional[str] = None
    vcs_id: Optional[str] = None
    iac_url_template: Optional[str] = None
    collect_job_id: Optional[str] = None
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    managed_resources_summary: ManagedResourcesSummaryDTO = None
    invalidation_info: List[InvalidationInfoDTO] = field(default_factory=list)
    iac_type: IacType = None
    workspace_id: Optional[str] = None
    cli_version: Optional[str] = None
    client: Optional[str] = None

    @staticmethod
    def get_steps():
        return [AssessmentStepDTO.COLLECT,
                AssessmentStepDTO.WAIT_FOR_CONTEXT,
                AssessmentStepDTO.WAIT_FOR_COLLECT,
                AssessmentStepDTO.PROCESS_STARTED,
                AssessmentStepDTO.PROCESS_RUNNING_TF_SHOW,
                AssessmentStepDTO.PROCESS_BUILDING_ENV_CONTEXT,
                AssessmentStepDTO.RUN_RULES,
                AssessmentStepDTO.RUN_CUSTOM_RULES,
                AssessmentStepDTO.SAVING_RESULTS]


@dataclass
class CspmAssessmentJobDTO(DataClassJsonMixin):
    id: str
    account_config_id: str
    customer_id: str
    run_status: RunStatusDTO
    last_step: Optional[AssessmentStepDTO] = None
    error_message: Optional[str] = None
    created_at: str = None
    ended_at: Optional[str] = None
    collect_job_id: Optional[str] = None
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    results_summary: ResultsSummaryDTO = None

    @staticmethod
    def get_steps():
        return [AssessmentStepDTO.PROCESS_STARTED,
                AssessmentStepDTO.PROCESS_BUILDING_ENV_CONTEXT,
                AssessmentStepDTO.RUN_RULES,
                AssessmentStepDTO.SAVING_RESULTS]
