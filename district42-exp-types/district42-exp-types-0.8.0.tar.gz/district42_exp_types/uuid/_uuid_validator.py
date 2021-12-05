from typing import Any
from uuid import UUID

from niltype import Nil, Nilable
from th import PathHolder
from valera import ValidationResult, Validator

from ._uuid_schema import UUIDSchema

__all__ = ("UUIDValidator",)


class UUIDValidator(Validator, extend=True):
    def visit_uuid(self, schema: UUIDSchema, *,
                   value: Any = Nil, path: Nilable[PathHolder] = Nil,
                   **kwargs: Any) -> ValidationResult:
        result = self._validation_result_factory()
        if path is Nil:
            path = self._path_holder_factory()

        if error := self._validate_type(path, value, UUID):
            return result.add_error(error)

        if schema.props.value is not Nil:
            if error := self._validate_value(path, value, schema.props.value):
                return result.add_error(error)

        return result
