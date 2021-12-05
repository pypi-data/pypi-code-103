from copy import deepcopy
from typing import Any

from district42.utils import is_ellipsis
from niltype import Nil, Nilable
from revolt import Substitutor, SubstitutorValidator
from revolt.errors import SubstitutionError, make_substitution_error
from th import PathHolder
from valera import ValidationResult
from valera.errors import LengthValidationError, MaxLengthValidationError, MinLengthValidationError

from ._unordered_schema import UnorderedSchema
from ._unordered_validator import UnorderedValidator

__all__ = ("UnorderedSubstitutor",)


class UnorderedSubstitutorValidator(SubstitutorValidator, extend=True):
    def visit_unordered(self, schema: UnorderedSchema, *,
                        value: Any = Nil, path: Nilable[PathHolder] = Nil,
                        **kwargs: Any) -> ValidationResult:
        result = self._validation_result_factory()
        if path is Nil:
            path = self._path_holder_factory()

        if error := self._validate_type(path, value, list):
            return result.add_error(error)

        if schema.props.len is not Nil:
            if len(value) != schema.props.len:
                return result.add_error(LengthValidationError(path, value, schema.props.len))
        if schema.props.min_len is not Nil:
            if len(value) < schema.props.min_len:
                return result.add_error(
                    MinLengthValidationError(path, value, schema.props.min_len))
        if schema.props.max_len is not Nil:
            if len(value) > schema.props.max_len:
                return result.add_error(
                    MaxLengthValidationError(path, value, schema.props.max_len))

        if (schema.props.type is Nil) and (schema.props.elements is Nil):
            return result

        if schema.props.type is not Nil:
            type_schema = schema.props.type
            for index, elem in enumerate(value):
                if is_ellipsis(elem) and (index == 0 or index == len(value) - 1):
                    continue
                nested_path = deepcopy(path)[index]
                res = type_schema.__accept__(self, value=elem, path=nested_path, **kwargs)
                result.add_errors(res.get_errors())
            return result

        # dirty area
        unordered_validator = UnorderedValidator(
            validation_result_factory=self._validation_result_factory,
            path_holder_factory=self._path_holder_factory,
        )
        return unordered_validator.visit_unordered(schema, value=value, path=path, **kwargs)


class UnorderedSubstitutor(Substitutor, extend=True):
    def visit_unordered(self, schema: UnorderedSchema, *,
                        value: Any = Nil,
                        **kwargs: Any) -> UnorderedSchema:
        result = schema.__accept__(self._validator, value=value)
        if result.has_errors():
            raise make_substitution_error(result, self._formatter)

        if len(value) > 0 and all(is_ellipsis(x) for x in value):
            raise SubstitutionError("Can't substitute all ...")

        if (schema.props.elements is Nil) and (schema.props.type is Nil):
            elements = []
            for val in value:
                element = val if is_ellipsis(val) else self._from_native(val)
                elements.append(element)
            return schema.__class__(schema.props.update(elements=elements))

        if schema.props.type is not Nil:
            elements = []
            for val in value:
                if is_ellipsis(val):
                    element = val
                else:
                    element = schema.props.type.__accept__(self, value=val, **kwargs)
                elements.append(element)
            return schema.__class__(schema.props.update(elements=elements, type=Nil))

        raise NotImplementedError()
