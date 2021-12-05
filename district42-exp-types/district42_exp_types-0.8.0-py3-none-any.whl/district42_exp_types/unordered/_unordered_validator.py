from copy import deepcopy
from typing import Any, Dict, List, cast

from district42 import GenericSchema
from district42.utils import is_ellipsis
from niltype import Nil, Nilable
from th import PathHolder
from valera import Formatter, ValidationResult, Validator
from valera.errors import (
    ExtraElementValidationError,
    LengthValidationError,
    MaxLengthValidationError,
    MinLengthValidationError,
    ValidationError,
)

from ._unordered_schema import UnorderedSchema

__all__ = ("UnorderedValidator", "UnorderedFormatter", "UnorderedContainsValidationError",)


class UnorderedContainsValidationError(ValidationError):
    def __init__(self, path: PathHolder, element: GenericSchema) -> None:
        self.path = path
        self.element = element

    def format(self, formatter: Formatter) -> str:
        return cast(str, formatter.format_unordered_error(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path!r}, {self.element!r})"


class UnorderedFormatter(Formatter, extend=True):
    def format_unordered_error(self, error: UnorderedContainsValidationError) -> str:
        formatted_path = self._at_path(error.path)
        return f"Value{formatted_path} must contain {error.element!r}"


class UnorderedValidator(Validator, extend=True):
    def _find_matches(self, validated: List[List[int]],
                      used: Dict[int, int], index: int = 0) -> Dict[int, int]:
        if len(validated) == 0:
            return used

        head, *tail = validated
        if len(head) == 0:
            res = self._find_matches(tail, {**used}, index + 1)
            return res if len(res) > len(used) else used

        result = used
        for val in head:
            if val in used:
                continue
            res = self._find_matches(tail, {**used, val: index}, index + 1)
            if len(res) > len(result):
                result = res
        return result

    def _validate_unordered_elements(self,
                                     path: PathHolder,
                                     values: List[Any],
                                     elements: List[GenericSchema],
                                     **kwargs: Any) -> Dict[int, int]:
        validated: List[List[int]] = [list() for _ in elements]
        for i, element in enumerate(elements):
            for j, value in enumerate(values):
                result = element.__accept__(self, value=value, path=path, **kwargs)
                if not result.has_errors():
                    validated[i].append(j)
        return self._find_matches(validated, {})

    def _validate_elements_missing(self, path: PathHolder, elements: List[GenericSchema],
                                   matches: Dict[int, int]) -> List[ValidationError]:
        matched_elements = set(matches.values())
        errors: List[ValidationError] = []
        for index, element in enumerate(elements):
            if index not in matched_elements:
                errors.append(UnorderedContainsValidationError(path, element))
        return errors

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
                nested_path = deepcopy(path)[index]
                res = type_schema.__accept__(self, value=elem, path=nested_path, **kwargs)
                result.add_errors(res.get_errors())
            return result

        elements = cast(List[GenericSchema], schema.props.elements)

        # body
        if (len(elements) > 2) and is_ellipsis(elements[0]) and is_ellipsis(elements[-1]):
            elements = elements[1:-1]
            matches = self._validate_unordered_elements(path, value, elements, **kwargs)
            errors = self._validate_elements_missing(path, elements, matches)
            return result.add_errors(errors)

        # head
        if (len(elements) >= 2) and is_ellipsis(elements[-1]):
            elements = elements[:-1]
            matches = self._validate_unordered_elements(path, value, elements, **kwargs)
            errors = self._validate_elements_missing(path, elements, matches)
            end = min(len(value), len(elements))
            for index in range(0, end):
                if index not in matches:
                    result.add_error(ExtraElementValidationError(path, value[index], index))
            return result.add_errors(errors)

        # tail
        if (len(elements) >= 1) and is_ellipsis(elements[0]):
            elements = elements[1:]
            matches = self._validate_unordered_elements(path, value, elements, **kwargs)
            start = max(0, len(value) - len(matches))
            for index in range(start, len(value)):
                if index not in matches:
                    result.add_error(ExtraElementValidationError(path, value[index], index))
            errors = self._validate_elements_missing(path, elements, matches)
            return result.add_errors(errors)

        matches = self._validate_unordered_elements(path, value, elements, **kwargs)
        errors = self._validate_elements_missing(path, elements, matches)
        result.add_errors(errors)

        for index, val in enumerate(value):
            if index not in matches:
                result.add_error(ExtraElementValidationError(path, val, index))

        return result
