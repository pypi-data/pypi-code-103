# -*- coding: utf-8 -*-
import enum
import inspect
import typing
import orjson

from pydantic import BaseModel
from pydantic import Extra
from pydantic.error_wrappers import ErrorWrapper
from pydantic.error_wrappers import ValidationError
from pydantic.fields import Field
from pydantic.fields import FieldInfo
from pydantic.fields import ModelField
from pydantic.fields import Undefined
from pydantic.main import BaseConfig
from pydantic.schema import default_ref_template
from pydantic.schema import field_type_schema
from pydantic.schema import get_field_info_schema
from pydantic.schema import get_flat_models_from_fields
from pydantic.schema import get_model_name_map
from pydantic.schema import model_type_schema as _model_type_schema
from werkzeug.datastructures import FileStorage

from basic_sdk.exceptions import InvalidRequest

_ = (Field,)


class _EnumError(object):
    def format(self, enum_values, **kwargs):
        values = ",".join([repr(v.value) for v in enum_values])
        return f"请输入({values})"


_CONST_TYPE_ERROR_TEMPLATES = {
    "integer": "请输入整数",
    "float": "请输入浮点数",
    "bool": "请输入布尔值",
    "str": "请输入字符串",
    "list": "请输入列表",
    "dict": "请输入字典",
    "enum": _EnumError(),
    "decimal": "请输入十进制数",
    "none.not_allowed": "不允许为 null",
}
_CONST_VALUE_ERROR_TEMPLATES = {
    "missing": "字段不能为空",
    "extra": "不允许传递该字段",
    "any_str.max_length": "字符串长度不能大于 {limit_value} 字符",
    "any_str.min_length": "字符串长度不能小于 {limit_value} 字符",
    "datetime": "日期时间格式错误",
    "date": "日期格式错误",
    "decimal.not_finite": "数字总位数不能超过 {max_digits} 位",
    "decimal.max_places": "小数点位数不能超过 {decimal_places} 位",
    "decimal.whole_digits": "整数位数不能超过 {whole_digits} 位",
    "duration": "时间格式错误",
    "email": "邮箱格式错误",
    "list.min_items": "列表最少包含 {limit_value} 个元素",
    "list.max_items": "列表最多包含 {limit_value} 个元素",
    "number.not_lt": "数据必须小于 {limit_value} ",
    "number.not_le": "数据必须小于等于 {limit_value}",
    "number.not_gt": "数据必须大于 {limit_value}",
    "number.not_ge": "数据必须大于等于 {limit_value}",
    "number.not_multiple": "数据必须是 {multiple_of} 的倍数",
    "str.regex": '字符串满足正则 "{pattern}"',
    "regex_pattern": "不是合法的正则表达式",
    "time": "时间格式错误",
}
_CONST_ERROR_TEMPLATES = {}
_CONST_ERROR_TEMPLATES.update(
    {f"type_error.{name}": error for name, error in _CONST_TYPE_ERROR_TEMPLATES.items()}
)
_CONST_ERROR_TEMPLATES.update(
    {
        f"value_error.{name}": error
        for name, error in _CONST_VALUE_ERROR_TEMPLATES.items()
    }
)


class Model(BaseModel):
    class Config:
        extra = Extra.forbid
        error_msg_templates = _CONST_ERROR_TEMPLATES
        json_loads = orjson.loads


class ModelIgnore:
    class Config:
        extra = Extra.forbid


class Source(FieldInfo):
    def __init__(
        self,
        alias: str = None,
        default: typing.Any = Undefined,
        required: bool = True,
        description: str = None,
        embed: bool = None,
        data_from: str = None,
        **kwargs,
    ):
        self.required = required
        self.embed = embed
        self.data_from = data_from
        super(Source, self).__init__(
            default=default,
            alias=alias,
            required=required,
            description=description,
            **kwargs,
        )


class File(FileStorage):
    @classmethod
    def __get_validators__(
        cls: typing.Type["File"],
    ) -> typing.Iterable[typing.Callable]:
        yield cls.validate

    @classmethod
    def validate(cls: typing.Type["File"], v: typing.Any) -> typing.Any:
        if not isinstance(v, FileStorage):
            raise ValueError(f"Expected UploadFile, received: {type(v)}")
        return v

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update({"type": "string", "format": "binary"})


def _format_error(error: dict):
    column = ""
    for loc in error["loc"]:
        if isinstance(loc, int):
            column = f"{column}[{loc}]"
        else:
            column = f"{column}.{loc}" if column else f"{loc}"
    error_type = "类型错误" if "type_error." in error["type"] else "数据错误"
    error_message = error["msg"]
    return f"字段 {column} {error_type}, {error_message}"


def is_list_type(_type: typing.Any):
    if isinstance(_type, list):
        return True
    origin = getattr(_type, "__origin__", None)
    if origin and isinstance(origin, type) and issubclass(origin, list):
        return True
    return False


def is_dict_type(_type):
    if isinstance(_type, dict):
        return True
    origin = getattr(_type, "__origin__", None)
    if origin and isinstance(origin, type) and issubclass(origin, dict):
        return True
    if isinstance(_type, type) and issubclass(_type, BaseModel):
        return True
    return False


def validate(
    value: typing.Any,
    name: str,
    source: Source,
    _type: typing.Any,
    loc: typing.Tuple[str, ...],
):
    required = source.required
    if source.default is not Undefined:
        required = False
    model_field = ModelField(
        name=name,
        type_=_type,
        class_validators={},
        model_config=BaseConfig,
        default=source.default,
        required=required,
        alias=source.alias or name,
        field_info=source,
    )
    if value is None and source.default is not Undefined:
        return source.default
    if value == "" and source.default == "":
        return value
    result, error = model_field.validate(value, {}, loc=loc)
    if not error:
        return result
    if isinstance(error, ErrorWrapper):
        error = [error]
    error = ValidationError(error, Model)
    errors = [_format_error(e) for e in error.errors()]
    raise InvalidRequest("\n".join(errors))


def get_models(name: str, source: Source, _type: typing.Any):
    model_field = ModelField(
        name=name,
        type_=_type,
        class_validators={},
        model_config=BaseConfig,
        default=source.default,
        required=source.required,
        alias=source.alias or name,
    )
    return get_flat_models_from_fields([model_field], known_models=set())


def get_models_map(models: set):
    return get_model_name_map(models)


def model_type_schema(
    model: typing.Type["BaseModel"],
    *,
    by_alias: bool,
    model_name_map: dict,
    ref_template: str,
    ref_prefix: str = None,
    known_models: set,
):
    if isinstance(model, type) and issubclass(model, enum.Enum):
        definitions = {
            "type": "string",
            "title": model.__name__,
            "description": inspect.getdoc(model),
            "enum": list(model.__members__.values()),
        }
        return definitions, {}, set()
    return _model_type_schema(
        model,
        by_alias=by_alias,
        model_name_map=model_name_map,
        ref_template=ref_template,
        ref_prefix=ref_prefix,
        known_models=known_models,
    )


def get_model_schema(
    name, model, source: Source = None, model_name_map=None, ref_prefix=""
):
    if isinstance(model, type) and issubclass(model, BaseModel):
        schema, _, _ = model_type_schema(
            model,
            by_alias=True,
            model_name_map=model_name_map,
            ref_prefix=ref_prefix,
            ref_template=default_ref_template,
            known_models={model},
        )
        return schema
    required = None
    if source:
        required = source.required
        if source.default is not Undefined:
            required = False
    if (
        hasattr(model, "__origin__")
        and getattr(model, "__origin__") is typing.Union
        and hasattr(model, "__args__")
    ):
        model_args = getattr(model, "__args__")
        if isinstance(model_args, tuple) and type(None) in model_args:
            required = False
    if source:
        source.required = required
        source.extra.update({"required": required})
    model_field = ModelField(
        name=name,
        type_=model,
        class_validators={},
        model_config=BaseConfig,
        default=source.default if source else None,
        required=required,
        alias=source.alias or name if source else None,
        field_info=source,
    )
    schema_info, status = get_field_info_schema(model_field)
    schema, _, _ = field_type_schema(
        model_field,
        by_alias=True,
        model_name_map=model_name_map,
        ref_prefix=ref_prefix,
        ref_template=default_ref_template,
        known_models=set(),
    )
    schema.update(schema_info)
    return schema


class AccountGroup(str, enum.Enum):
    shop = "shop"
    channel = "channel"
