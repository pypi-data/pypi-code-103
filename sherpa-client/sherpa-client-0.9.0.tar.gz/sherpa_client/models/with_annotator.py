from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.with_annotator_condition import WithAnnotatorCondition
from ..models.with_annotator_parameters import WithAnnotatorParameters
from ..types import UNSET, Unset

T = TypeVar("T", bound="WithAnnotator")


@attr.s(auto_attribs=True)
class WithAnnotator:
    """ """

    annotator: str
    disabled: Union[Unset, bool] = UNSET
    project_name: Union[Unset, str] = UNSET
    parameters: Union[Unset, WithAnnotatorParameters] = UNSET
    condition: Union[Unset, WithAnnotatorCondition] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        annotator = self.annotator
        disabled = self.disabled
        project_name = self.project_name
        parameters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        condition: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.condition, Unset):
            condition = self.condition.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "annotator": annotator,
            }
        )
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if project_name is not UNSET:
            field_dict["projectName"] = project_name
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if condition is not UNSET:
            field_dict["condition"] = condition

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        annotator = d.pop("annotator")

        disabled = d.pop("disabled", UNSET)

        project_name = d.pop("projectName", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: Union[Unset, WithAnnotatorParameters]
        if isinstance(_parameters, Unset):
            parameters = UNSET
        else:
            parameters = WithAnnotatorParameters.from_dict(_parameters)

        _condition = d.pop("condition", UNSET)
        condition: Union[Unset, WithAnnotatorCondition]
        if isinstance(_condition, Unset):
            condition = UNSET
        else:
            condition = WithAnnotatorCondition.from_dict(_condition)

        with_annotator = cls(
            annotator=annotator,
            disabled=disabled,
            project_name=project_name,
            parameters=parameters,
            condition=condition,
        )

        return with_annotator
