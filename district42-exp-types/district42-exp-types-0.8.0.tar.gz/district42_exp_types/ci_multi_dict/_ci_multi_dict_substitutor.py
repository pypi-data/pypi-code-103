from copy import deepcopy
from typing import Any, List

from district42 import GenericSchema
from multidict import CIMultiDict
from niltype import Nil, Nilable
from revolt import Substitutor, SubstitutorValidator
from revolt.errors import SubstitutionError, make_substitution_error
from th import PathHolder
from valera import ValidationResult
from valera.errors import ExtraKeyValidationError, ValidationError

from ._ci_multi_dict_schema import CIMultiDictSchema
from ._utils import get_unique_keys

__all__ = ("CIMultiDictSubstitutor", "CIMultiDictSubstitutorValidator",)


class CIMultiDictSubstitutor(Substitutor, extend=True):
    def visit_ci_multi_dict(self, schema: CIMultiDictSchema, *,
                            value: Any = Nil, **kwargs: Any) -> CIMultiDictSchema:
        if not isinstance(value, CIMultiDict):
            try:
                value = CIMultiDict(value)
            except Exception as e:
                message = f"Can't substitute to MultiDict: {e}"
                raise SubstitutionError(message)

        result = schema.__accept__(self._validator, value=value)
        if result.has_errors():
            raise make_substitution_error(result, self._formatter)

        keys = CIMultiDict[GenericSchema]()
        if schema.props.keys is Nil:
            for key, val in value.items():
                keys.add(key, self._from_native(val))
            return schema.__class__(schema.props.update(keys=keys))

        for key in get_unique_keys(schema.props.keys):
            if key not in value:
                for val in schema.props.keys.getall(key):
                    keys.add(key, val)
                continue

            values = schema.props.keys.getall(key)
            candidates = value.getall(key)
            for candidate in candidates:
                for idx, val in enumerate(values):
                    try:
                        sch = val.__accept__(self, value=candidate, **kwargs)
                    except SubstitutionError:
                        pass
                    else:
                        values[idx] = sch
            for val in values:
                keys.add(key, val)

        return schema.__class__(schema.props.update(keys=keys))


class CIMultiDictSubstitutorValidator(SubstitutorValidator, extend=True):
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

        if schema.props.keys is Nil:
            return result

        for key in get_unique_keys(schema.props.keys):
            if key not in value:
                continue
            candidates = value.getall(key)
            nested_path = deepcopy(path)[key]
            for val in schema.props.keys.getall(key):
                errors = self.__validate_candidates(val, nested_path, candidates, **kwargs)
                result.add_errors(errors)

        for key in get_unique_keys(value):
            if key not in schema.props.keys:
                result.add_error(ExtraKeyValidationError(path, value, key))
            else:
                vals = value.getall(key)
                if len(vals) > len(schema.props.keys.getall(key)):
                    result.add_error(ExtraKeyValidationError(path, value, key))

        return result
