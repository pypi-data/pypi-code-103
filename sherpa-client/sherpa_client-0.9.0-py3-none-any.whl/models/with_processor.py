from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.with_processor_condition import WithProcessorCondition
from ..models.with_processor_parameters import WithProcessorParameters
from ..types import UNSET, Unset

T = TypeVar("T", bound="WithProcessor")


@attr.s(auto_attribs=True)
class WithProcessor:
    """ """

    processor: str
    disabled: Union[Unset, bool] = UNSET
    parameters: Union[Unset, WithProcessorParameters] = UNSET
    condition: Union[Unset, WithProcessorCondition] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        processor = self.processor
        disabled = self.disabled
        parameters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        condition: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.condition, Unset):
            condition = self.condition.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "processor": processor,
            }
        )
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if condition is not UNSET:
            field_dict["condition"] = condition

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        processor = d.pop("processor")

        disabled = d.pop("disabled", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: Union[Unset, WithProcessorParameters]
        if isinstance(_parameters, Unset):
            parameters = UNSET
        else:
            parameters = WithProcessorParameters.from_dict(_parameters)

        _condition = d.pop("condition", UNSET)
        condition: Union[Unset, WithProcessorCondition]
        if isinstance(_condition, Unset):
            condition = UNSET
        else:
            condition = WithProcessorCondition.from_dict(_condition)

        with_processor = cls(
            processor=processor,
            disabled=disabled,
            parameters=parameters,
            condition=condition,
        )

        return with_processor
