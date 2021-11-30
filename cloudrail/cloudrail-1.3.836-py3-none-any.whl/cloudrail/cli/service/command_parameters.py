import sys
from dataclasses import dataclass
from typing import Optional
from common.api.dtos.assessment_job_dto import RunOriginDTO
from cloudrail.knowledge.context.iac_type import IacType 


@dataclass
class CommandParameters:
    no_fail_on_service_error: bool = None
    upload_log: bool = False
    no_upload_log: bool = False
    origin: RunOriginDTO = RunOriginDTO.WORKSTATION
    notty: bool = None
    is_tty: bool = None
    iac_type: IacType = IacType.TERRAFORM
    aws_default_region: Optional[str] = None
    raw: bool = None


    def __post_init__(self):
        self.is_tty = self.origin != RunOriginDTO.CI and not self.notty and sys.stdout.isatty()
