from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.sherpa_job_bean_status import SherpaJobBeanStatus
from ..models.sherpa_job_bean_type import SherpaJobBeanType
from ..types import UNSET, Unset

T = TypeVar("T", bound="SherpaJobBean")


@attr.s(auto_attribs=True)
class SherpaJobBean:
    """ """

    project: str
    project_label: str
    id: str
    type: SherpaJobBeanType
    upload_ids: List[str]
    description: str
    status: SherpaJobBeanStatus
    created_at: int
    created_by: str
    total_step_count: int
    current_step_count: int
    status_message: Union[Unset, str] = UNSET
    completed_at: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        project = self.project
        project_label = self.project_label
        id = self.id
        type = self.type.value

        upload_ids = self.upload_ids

        description = self.description
        status = self.status.value

        created_at = self.created_at
        created_by = self.created_by
        total_step_count = self.total_step_count
        current_step_count = self.current_step_count
        status_message = self.status_message
        completed_at = self.completed_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "project": project,
                "projectLabel": project_label,
                "id": id,
                "type": type,
                "uploadIds": upload_ids,
                "description": description,
                "status": status,
                "createdAt": created_at,
                "createdBy": created_by,
                "totalStepCount": total_step_count,
                "currentStepCount": current_step_count,
            }
        )
        if status_message is not UNSET:
            field_dict["statusMessage"] = status_message
        if completed_at is not UNSET:
            field_dict["completedAt"] = completed_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        project = d.pop("project")

        project_label = d.pop("projectLabel")

        id = d.pop("id")

        type = SherpaJobBeanType(d.pop("type"))

        upload_ids = cast(List[str], d.pop("uploadIds"))

        description = d.pop("description")

        status = SherpaJobBeanStatus(d.pop("status"))

        created_at = d.pop("createdAt")

        created_by = d.pop("createdBy")

        total_step_count = d.pop("totalStepCount")

        current_step_count = d.pop("currentStepCount")

        status_message = d.pop("statusMessage", UNSET)

        completed_at = d.pop("completedAt", UNSET)

        sherpa_job_bean = cls(
            project=project,
            project_label=project_label,
            id=id,
            type=type,
            upload_ids=upload_ids,
            description=description,
            status=status,
            created_at=created_at,
            created_by=created_by,
            total_step_count=total_step_count,
            current_step_count=current_step_count,
            status_message=status_message,
            completed_at=completed_at,
        )

        return sherpa_job_bean
