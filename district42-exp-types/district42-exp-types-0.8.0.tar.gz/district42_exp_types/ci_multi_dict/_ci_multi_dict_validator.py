from copy import deepcopy
from typing import Any, List, Mapping

from district42 import GenericSchema
from multidict import CIMultiDict, CIMultiDictProxy
from niltype import Nil, Nilable
from th import PathHolder
from valera import ValidationResult, Validator
from valera.errors import (
    ExtraKeyValidationError,
    MissingKeyValidationError,
    TypeValidationError,
    ValidationError,
)

from ._ci_multi_dict_schema import CIMultiDictSchema
from ._utils import get_unique_keys

__all__ = ("CIMultiDictValidator",)


class CIMultiDictValidator(Validator, extend=True):
    def __validate_candidates(self, value: GenericSchema, path: PathHolder,
                              candidates: List[Any], **kwargs: Any) -> List[ValidationError]:
        all_errors = []
        for candidate in candidates:
            res = value.__accept__(self, value=candidate, path=path, **kwargs)
            if not res.has_errors():
                return []
            all_errors.append(res.get_errors())
        all_errors.sort(key=len)
        return all_errors[0]

    def visit_ci_multi_dict(self, schema: CIMultiDictSchema, *,
                            value: Any = Nil, path: Nilable[PathHolder] = Nil,
                            **kwargs: Any) -> ValidationResult:
        result = self._validation_result_factory()
        if path is Nil:
            path = self._path_holder_factory()

        if not isinstance(value, Mapping):
            return result.add_error(TypeValidationError(path, value, Mapping))

        if schema.props.keys is Nil:
            return result

        for key in get_unique_keys(schema.props.keys):
            if key not in value:
                result.add_error(MissingKeyValidationError(path, value, key))
                continue

            nested_path = deepcopy(path)[key]
            if isinstance(value, (CIMultiDict, CIMultiDictProxy)):
                candidates = value.getall(key)
                for val in schema.props.keys.getall(key):
                    errors = self.__validate_candidates(val, nested_path, candidates, **kwargs)
                    result.add_errors(errors)
            else:
                val = schema.props.keys.getone(key)
                res = val.__accept__(self, value=value[key], path=nested_path, **kwargs)
                result.add_errors(res.get_errors())

        for key in get_unique_keys(value):
            if key not in schema.props.keys:
                result.add_error(ExtraKeyValidationError(path, value, key))
            else:
                if isinstance(value, (CIMultiDict, CIMultiDictProxy)):
                    vals = value.getall(key)
                else:
                    vals = [value.get(key)]
                if len(vals) > len(schema.props.keys.getall(key)):
                    result.add_error(ExtraKeyValidationError(path, value, key))

        return result
