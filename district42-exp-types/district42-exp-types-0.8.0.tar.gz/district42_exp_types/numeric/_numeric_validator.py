from typing import Any

from niltype import Nil, Nilable
from th import PathHolder
from valera import ValidationResult, Validator
from valera.errors import MaxValueValidationError, MinValueValidationError

from ._numeric_schema import NumericSchema

__all__ = ("NumericValidator",)


class NumericValidator(Validator, extend=True):
    def visit_numeric(self, schema: NumericSchema, *,
                      value: Any = Nil, path: Nilable[PathHolder] = Nil,
                      **kwargs: Any) -> ValidationResult:
        result = self._validation_result_factory()
        if path is Nil:
            path = self._path_holder_factory()

        if error := self._validate_type(path, value, str):
            return result.add_error(error)

        if schema.props.value is not Nil:
            if error := self._validate_value(path, value, schema.props.value):
                return result.add_error(error)

        if schema.props.min is not Nil:
            if int(value) < int(schema.props.min):
                result.add_error(MinValueValidationError(path, value, schema.props.min))

        if schema.props.max is not Nil:
            if int(value) > int(schema.props.max):
                result.add_error(MaxValueValidationError(path, value, schema.props.max))

        return result
