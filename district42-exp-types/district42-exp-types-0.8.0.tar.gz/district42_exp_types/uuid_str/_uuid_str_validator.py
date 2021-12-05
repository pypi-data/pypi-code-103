from typing import Any, cast
from uuid import UUID

from niltype import Nil, Nilable
from th import PathHolder
from valera import Formatter, ValidationResult, Validator
from valera.errors import TypeValidationError, ValidationError, ValueValidationError

from ._uuid_str_schema import UUIDStrSchema

__all__ = ("UUIDStrValidator", "StrCaseValidationError", "StrCaseFormatter",)


class StrCaseValidationError(ValidationError):
    def __init__(self, path: PathHolder, actual_value: str, expected_case: str) -> None:
        self.path = path
        self.actual_value = actual_value
        self.expected_case = expected_case

    def format(self, formatter: Formatter) -> str:
        return cast(str, formatter.format_str_case_error(self))

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}({self.path!r}, {self.actual_value!r}, "
                f"{self.expected_case!r})")


class StrCaseFormatter(Formatter, extend=True):
    def format_str_case_error(self, error: StrCaseValidationError) -> str:
        actual_type = self._get_type(error.actual_value)
        formatted_path = self._at_path(error.path)
        return (f"Value {actual_type}{formatted_path} "
                f"must be in {error.expected_case} case, but {error.actual_value!r} given")


class UUIDStrValidator(Validator, extend=True):
    def visit_uuid_str(self, schema: UUIDStrSchema, *,
                       value: Any = Nil, path: Nilable[PathHolder] = Nil,
                       **kwargs: Any) -> ValidationResult:
        result = self._validation_result_factory()
        if path is Nil:
            path = self._path_holder_factory()

        if error := self._validate_type(path, value, str):
            return result.add_error(error)

        try:
            actual_value = UUID(value)
        except (TypeError, ValueError):
            if schema.props.value is not Nil:
                error = ValueValidationError(path, value, schema.props.value)
            else:
                error = TypeValidationError(path, value, UUID)
            return result.add_error(error)

        if schema.props.value is not Nil:
            if actual_value != UUID(schema.props.value):
                error = ValueValidationError(path, value, schema.props.value)
                return result.add_error(error)

        if schema.props.is_lowercase is not Nil:
            if not value.islower():
                error = StrCaseValidationError(path, value, str.lower.__name__)
                return result.add_error(error)

        if schema.props.is_uppercase is not Nil:
            if not value.isupper():
                error = StrCaseValidationError(path, value, str.upper.__name__)
                return result.add_error(error)

        return result
