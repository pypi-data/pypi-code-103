from typing import Any

from .utils import Container, ContainerField


class FieldValidationError(Exception):
    def __init__(self, error_code: str):
        super().__init__()
        self.error_code = error_code

class Field(ContainerField):
    ERROR_REQUIRED = 'required'

    def __init__(self, *args: Any, required: bool = True, default: Any | None = None, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.required = required
        if self.required and default:
            raise UserWarning('Cannot set default for required field')

        self.default = default

    def run_validation(self, value: str) -> Any | None: # pylint: disable=no-self-use
        return value # pragma: no cover

    def validate(self, value: Any) -> Any | None:
        if value:
            return self.run_validation(value)

        if self.required:
            raise FieldValidationError(self.ERROR_REQUIRED)

        return self.default

class FormValidationError(Exception):
    def __init__(self, field_errors: dict[str, FieldValidationError]):
        super().__init__()
        self.errors = field_errors


FormData = dict[str, Any]
FormErrors = dict[str, FieldValidationError]
class Form(Container):
    FIELD_BASE_CLASS = Field
    RESERVED_ATTRS = ['is_validated', 'errors', 'data']

    def __init__(self, data: FormData | object, *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)

        self._raw_data: FormData | object = data
        self._data: FormData = {}
        self._errors: FormErrors = {}

    @property
    def is_validated(self) -> bool:
        return len(self._data.keys()) > 0 or len(self._errors.keys()) > 0

    @property
    def errors(self) -> FormErrors:
        assert self.is_validated, 'Form hasn\'t been validated'
        return self._errors

    @property
    def data(self) -> FormData:
        assert self.is_validated, 'Form hasn\'t been validated'
        return self._data

    def add_error(self, field_name: str, error: FieldValidationError) -> None:
        self.errors[field_name] = error

    async def run_validation(self) -> None:
        pass

    async def validate(self) -> None:
        self._data = {}
        self._errors = {}

        for field_name, field_value, field in self._field_values(self._raw_data):
            try:
                self._data[field_name] = field.validate(field_value)
            except FieldValidationError as validation_error:
                self._errors[field_name] = validation_error

        await self.run_validation()

        if len(self._errors) > 0:
            self._data = {}
            raise FormValidationError(self._errors)

    async def is_valid(self) -> bool:
        if not self.is_validated:
            try:
                await self.validate()
            except FormValidationError as _exc:
                pass

        return len(self._errors) == 0
