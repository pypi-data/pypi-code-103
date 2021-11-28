from copy import deepcopy
from typing import Any, cast

from district42 import GenericSchema
from jj.mock import HistoryRequest
from niltype import Nil, Nilable
from th import PathHolder
from valera import ValidationResult, Validator
from valera.errors import ExtraKeyValidationError, TypeValidationError

from ._history_request_schema import HistoryRequestSchema

__all__ = ("HistoryRequestValidator",)


class HistoryRequestValidator(Validator, extend=True):
    def visit_jj_history_request(self, schema: HistoryRequestSchema, *,
                                 value: Any = Nil, path: Nilable[PathHolder] = Nil,
                                 **kwargs: Any) -> ValidationResult:
        result = self._validation_result_factory()
        if path is Nil:
            path = self._path_holder_factory()

        if isinstance(value, HistoryRequest):
            for key in schema.props:
                nested_path = deepcopy(path)[key]
                sch = cast(GenericSchema, schema.props.get(key))
                res = sch.__accept__(self, value=getattr(value, key), path=nested_path, **kwargs)
                result.add_errors(res.get_errors())
            return result

        if isinstance(value, dict):
            for key in schema.props:
                if key not in value:
                    continue
                nested_path = deepcopy(path)[key]
                sch = cast(GenericSchema, schema.props.get(key))
                res = sch.__accept__(self, value=value[key], path=nested_path, **kwargs)
                result.add_errors(res.get_errors())

            for key in value:
                if key not in schema.props:
                    result.add_error(ExtraKeyValidationError(path, value, key))

            return result

        return result.add_error(TypeValidationError(PathHolder(), value, HistoryRequest))
