from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="OperationCount")


@attr.s(auto_attribs=True)
class OperationCount:
    """Annotation creation response"""

    operation: str
    unit: str
    count: int

    def to_dict(self) -> Dict[str, Any]:
        operation = self.operation
        unit = self.unit
        count = self.count

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "operation": operation,
                "unit": unit,
                "count": count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        operation = d.pop("operation")

        unit = d.pop("unit")

        count = d.pop("count")

        operation_count = cls(
            operation=operation,
            unit=unit,
            count=count,
        )

        return operation_count
