from dataclasses import dataclass

from cloudrail.knowledge.context.iac_type import IacType
from dataclasses_json import DataClassJsonMixin

from common.api.dtos.assessment_job_dto import ResultsSummaryDTO, RunOriginDTO
from common.api.dtos.cloud_provider_dto import CloudProviderDTO


@dataclass
class IacAssessmentResultDTO(DataClassJsonMixin):
    id: str
    account_config_id: str
    created_at: str
    origin: RunOriginDTO
    build_link: str
    execution_source_identifier: str
    vcs_id: str
    iac_url_template: str
    results_summary: ResultsSummaryDTO
    cloud_provider: CloudProviderDTO
    assessment_name: str
    iac_type: IacType
