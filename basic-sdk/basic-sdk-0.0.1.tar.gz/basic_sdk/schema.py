# -*- coding: utf-8 -*-
# @File    : schema.py
# @Time    : 2021/11/26 4:43 下午


# -*- coding: utf-8 -*-

from collections import OrderedDict
import enum
import re
import typing

import orjson

from basic_sdk.exceptions import SchemaError


def orjson_loads(s):
    return orjson.loads(s)


def orjson_dumps(obj, *, default=None):
    return orjson.dumps(obj, default=default).decode()


class JSON(dict):
    def __init__(self, content: typing.Union[str, bytes]):
        try:
            data = orjson_loads(content)
            if not isinstance(data, dict):
                raise SchemaError("请求数据格式错误,请输入字典")
        except orjson.JSONDecodeError:
            raise SchemaError("请求数据格式错误,请输入字典")
        super(JSON, self).__init__(**data)


class LIST(list):
    def __init__(self, content: typing.Union[str, bytes]):
        try:
            data = orjson_loads(content)
            if not isinstance(data, list):
                raise SchemaError("请求数据格式错误, 请输入列表")
        except orjson.JSONDecodeError:
            raise SchemaError("请求数据格式错误, 请输入列表")
        super(LIST, self).__init__(data)


class RequestInvalid(SchemaError):
    def __init__(self, error: str):
        self.error = error


class DATA(str, enum.Enum):
    JSON = "JSON"
    PATH = "PATH"
    QUERY = "QUERY"
    HEADER = "HEADER"
    COOKIE = "COOKIE"
    FORM = "FORM"


class Type(object):
    def __init__(
        self,
        nullable: bool = False,
        default: typing.Any = None,
        description: str = None,
        data_from: str = None,
    ):
        self.nullable = nullable
        self.default = default
        self.description = description
        self.data_from = data_from
        if data_from:
            self.data_from = DATA(data_from)

    def __call__(self, value: typing.Any, name: str = "") -> typing.Any:
        pass

    def get_schema(self) -> dict:
        pass


class Boolean(Type):
    errors = {
        "type": "字段 {name} 类型错误 请输入布尔类型",
    }

    BOOL_FALSE = {0, "0", "off", "f", "false", "n", "no"}
    BOOL_TRUE = {1, "1", "on", "t", "true", "y", "yes"}

    def __call__(self, value: typing.Any, name: str = "") -> typing.Optional[bool]:
        if self.default is not None and value is None:
            return self.default
        if self.nullable and value is None:
            return value
        if value is True or value is False:
            return value
        if isinstance(value, bytes):
            value = value.decode()
        if isinstance(value, str):
            value = value.lower()
        try:
            if value in self.BOOL_TRUE:
                return True
            if value in self.BOOL_FALSE:
                return False
        except TypeError:
            pass
        raise RequestInvalid(self.errors["type"].format(name=name))

    def get_schema(self) -> dict:
        return dict(
            type="boolean",
            data_from=self.data_from,
            nullable=self.nullable,
            description=self.description,
            default=self.default,
        )


class Integer(Type):
    errors = {
        "type": "字段 {name} 类型错误 请输入整数",
        "min_num": "字段 {name} 不能小于 {min_num}",
        "max_num": "字段 {name} 不能大于 {max_num}",
    }

    def __init__(
        self,
        min_num: int = None,
        max_num: int = None,
        strict: bool = False,
        nullable: bool = False,
        default: int = None,
        description: str = None,
        data_from: str = None,
    ):
        super(Integer, self).__init__(
            nullable=nullable,
            default=default,
            description=description,
            data_from=data_from,
        )
        self.min_num = min_num
        self.max_num = max_num
        self.strict = strict

    def __call__(self, value: typing.Any, name: str = "") -> typing.Optional[int]:
        if self.default is not None and value is None:
            return self.default
        if self.nullable and (value is None or value == ""):
            return 0
        if self.strict and not isinstance(value, int):
            raise RequestInvalid(self.errors["type"].format(name=name))
        try:
            value = int(value)
        except (TypeError, ValueError, Exception):
            raise RequestInvalid(self.errors["type"].format(name=name))
        if self.min_num is not None and value < self.min_num:
            raise RequestInvalid(
                self.errors["min_num"].format(name=name, min_num=self.min_num)
            )
        if self.max_num is not None and value > self.max_num:
            raise RequestInvalid(
                self.errors["max_num"].format(name=name, max_num=self.max_num)
            )
        return value

    def get_schema(self) -> dict:
        extra = []
        if self.min_num is not None:
            extra.append(f"最小值为: {self.min_num}")
        if self.max_num is not None:
            extra.append(f"最大值为: {self.max_num}")
        return dict(
            type="integer",
            data_from=self.data_from,
            nullable=self.nullable,
            description=self.description,
            extra=", ".join(extra),
            default=self.default,
        )


class Float(Type):
    type = float
    errors = {
        "type": "字段 {name} 类型错误 请输入浮点数",
        "min_num": "字段 {name} 不能小于 {min_num}",
        "max_num": "字段 {name} 不能大于 {max_num}",
    }

    def __init__(
        self,
        min_num: int = None,
        max_num: int = None,
        strict: bool = False,
        nullable: bool = False,
        default: float = None,
        description: str = None,
        data_from: str = None,
    ):
        super(Float, self).__init__(
            nullable=nullable,
            default=default,
            description=description,
            data_from=data_from,
        )
        self.min_num = min_num
        self.max_num = max_num
        self.strict = strict

    def __call__(self, value: typing.Any, name: str = "") -> typing.Optional[float]:
        if self.default is not None and value is None:
            return self.default
        if self.nullable and (value is None or value == ""):
            return 0.0
        if self.strict and not isinstance(value, float):
            raise RequestInvalid(self.errors["type"].format(name=name))
        try:
            value = float(value)
        except (TypeError, ValueError, Exception):
            raise RequestInvalid(self.errors["type"].format(name=name))
        if self.min_num is not None and value < self.min_num:
            raise RequestInvalid(
                self.errors["min_num"].format(name=name, min_num=self.min_num)
            )
        if self.max_num is not None and value > self.max_num:
            raise RequestInvalid(
                self.errors["max_num"].format(name=name, max_num=self.max_num)
            )
        return value

    def get_schema(self) -> dict:
        extra = []
        if self.min_num is not None:
            extra.append(f"最小值为: {self.min_num}")
        if self.max_num is not None:
            extra.append(f"最大值为: {self.max_num}")
        return dict(
            type="double",
            data_from=self.data_from,
            nullable=self.nullable,
            description=self.description,
            extra=", ".join(extra),
            default=self.default,
        )


class String(Type):
    errors = {
        "type": "字段 {name} 类型错误 请输入字符串",
        "min_length": "字段 {name} 字符串长度不能小于 {min_length}",
        "max_length": "字段 {name} 字符串长度不能大于 {max_length}",
        "regex": "字段 {name} 字符串 {error}",
    }

    def __init__(
        self,
        min_length: int = None,
        max_length: int = None,
        regexes: typing.List[typing.Tuple[str, str]] = None,
        nullable: bool = False,
        default: str = None,
        description: str = None,
        data_from: str = None,
    ):
        super(String, self).__init__(
            nullable=nullable,
            default=default,
            description=description,
            data_from=data_from,
        )
        self.min_length = min_length
        self.max_length = max_length
        self.regexes = [
            (re.compile(pattern), error) for pattern, error in regexes or []
        ]

    def __call__(self, value: typing.Any, name: str = "") -> typing.Optional[str]:
        if self.default is not None and value is None:
            return self.default
        if self.nullable and value is None:
            return value
        if isinstance(value, int):
            value = str(value)
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if not isinstance(value, str):
            raise RequestInvalid(self.errors["type"].format(name=name))
        try:
            value = str(value)
        except (TypeError, Exception):
            raise RequestInvalid(self.errors["type"].format(name=name))
        if self.min_length is not None and len(value) < self.min_length:
            raise RequestInvalid(
                self.errors["min_length"].format(name=name, min_length=self.min_length)
            )
        if self.max_length is not None and len(value) > self.max_length:
            raise RequestInvalid(
                self.errors["max_length"].format(name=name, max_length=self.max_length)
            )
        if self.regexes:
            for regex, error in self.regexes:
                if not regex.fullmatch(value):
                    raise RequestInvalid(
                        self.errors["regex"].format(name=name, error=error)
                    )
        return value

    def get_schema(self) -> dict:
        extra = []
        if self.min_length is not None:
            extra.append(f"最小长度为: {self.min_length}")
        if self.max_length is not None:
            extra.append(f"最大长度为: {self.max_length}")
        for patter, error in self.regexes:
            extra.append(error)
        return dict(
            type="string",
            data_from=self.data_from,
            nullable=self.nullable,
            description=self.description,
            extra=", ".join(extra),
            default=self.default,
        )


class List(Type):
    errors = {
        "type": "字段 {name} 类型错误 请输入列表",
        "min_length": "字段 {name} 列表长度不能小于 {min_length}",
        "max_length": "字段 {name} 列表长度不能大于 {max_length}",
    }

    def __init__(
        self,
        column: Type,
        min_length: int = None,
        max_length: int = None,
        nullable: bool = False,
        default: list = None,
        description: str = None,
        data_from: str = None,
    ):
        super(List, self).__init__(
            nullable=nullable,
            default=default,
            description=description,
            data_from=data_from,
        )
        self.column = column
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value: typing.Any, name: str = "") -> typing.Optional[list]:
        if self.default is not None and value is None:
            return self.default
        if self.nullable and value is None:
            return value
        if not isinstance(value, list):
            raise RequestInvalid(self.errors["type"].format(name=name))
        items = []
        for index, v in enumerate(value):
            items.append(self.column(value=v, name=f"{name}[{index}]"))
        return items

    def get_schema(self) -> dict:
        extra = []
        if self.min_length is not None:
            extra.append(f"最小长度为: {self.min_length}")
        if self.max_length is not None:
            extra.append(f"最大长度为: {self.max_length}")
        return dict(
            type="array",
            type_class=self.column.__class__.__name__,
            items=self.column.get_schema(),
            data_from=self.data_from,
            nullable=self.nullable,
            description=self.description,
            extra=", ".join(extra),
            default=self.default,
        )


class Map(Type):
    errors = {
        "type": "字段 {name} 类型错误 请输入字典",
    }

    def __init__(
        self,
        columns: typing.Dict[str, Type] = None,
        keep_unknown: bool = False,
        nullable: bool = False,
        default: dict = None,
        description: str = None,
        data_from: str = None,
    ):
        super(Map, self).__init__(
            nullable=nullable,
            default=default,
            description=description,
            data_from=data_from,
        )
        self.columns = columns or {}
        self.keep_unknown = keep_unknown

    def __call__(self, value: typing.Any, name: str = "") -> typing.Optional[dict]:
        if self.default is not None and value is None:
            return self.default
        if self.nullable and value is None:
            return value
        if not isinstance(value, dict):
            raise RequestInvalid(self.errors["type"].format(name=name))
        value = {**value}
        data = AttrDict()
        for column, type_ in self.columns.items():
            v = type_(
                value=value.pop(column, None),
                name=f"{name}.{column}" if name else f"{column}",
            )
            if getattr(type_, "nullable", False) and v is None:
                continue
            data[column] = v
        if self.keep_unknown:
            data.update(value)
        return data

    def get_schema(self) -> dict:
        extra = []
        if self.keep_unknown:
            extra.append("保留未知字段")
        return dict(
            type="object",
            type_class="Dict",
            properties={name: tp.get_schema() for name, tp in self.columns.items()},
            data_from=self.data_from,
            nullable=self.nullable,
            description=self.description,
            extra=", ".join(extra),
            default=self.default,
        )


class Union(Type):
    errors = {"type": "字段 {name} 类型错误 请输入 ({type_names})"}

    def __init__(
        self,
        *types: Type,
        nullable: bool = False,
        default: dict = None,
        description: str = None,
        data_from: str = None,
    ):
        assert len(types) >= 1, "at least one union type required"
        for tp in types:
            assert isinstance(tp, Type), "types must be Type instance"
        super(Union, self).__init__(
            nullable=nullable,
            default=default,
            description=description,
            data_from=data_from,
        )
        self.types = types
        self.type_names = " 或 ".join([tp.__class__.__name__ for tp in types])
        self.many = len(types) > 1

    def __call__(self, value: typing.Any, name: str = "") -> typing.Any:
        if self.default is not None and value is None:
            return self.default
        if self.nullable and value is None:
            return value
        for type_ in self.types:
            try:
                return type_(value=value, name=name)
            except RequestInvalid as e:
                if not self.many:
                    raise
        raise RequestInvalid(
            self.errors["type"].format(name=name, type_names=self.type_names)
        )

    def get_schema(self) -> dict:
        raise RuntimeError("TODO")


class Any(Type):
    def __call__(self, value: typing.Any, name: str = "") -> typing.Any:
        return value

    def get_schema(self) -> dict:
        return dict(
            type=self.__class__.__name__,
            data_from=self.data_from,
            nullable=self.nullable,
            description=self.description,
            default=self.default,
        )


class File(Type):
    def __call__(self, value: typing.Any, name: str = "") -> typing.Any:
        return value

    def get_schema(self) -> dict:
        return dict(
            type="string",
            type_class="File",
            format="binary",
            data_from=self.data_from,
            nullable=self.nullable,
            description=self.description,
            default=self.default,
        )


class Enum(Type):
    errors = {"type": "字段 {name} 数据错误 只能是 ({enum_values})"}

    def __init__(
        self,
        enums: enum.EnumMeta,
        nullable: bool = False,
        default: dict = None,
        description: str = None,
        data_from: str = None,
    ):
        super(Enum, self).__init__(
            nullable=nullable,
            default=default,
            description=description,
            data_from=data_from,
        )
        self.enums = enums
        self.enum_values = " 或 ".join(self.enums.__members__.values())

    def __call__(self, value: typing.Any, name: str = "") -> typing.Optional[enum.Enum]:
        if self.default is not None and value is None:
            return self.default
        if self.nullable and value is None:
            return value
        try:
            return self.enums(value)
        except ValueError:
            raise RequestInvalid(
                self.errors["type"].format(name=name, enum_values=self.enum_values)
            )

    def get_schema(self) -> dict:
        return dict(
            type="string",
            enum=list(self.enums.__members__.values()),
            data_from=self.data_from,
            nullable=self.nullable,
            description=self.description,
            default=self.default,
            extra=f"只能是 ({self.enum_values})",
        )


class _MapMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == "Schema":
            return type.__new__(cls, name, bases, attrs)
        fields = OrderedDict()
        for base in bases:
            if not issubclass(base, Schema):
                continue
            for column, type_ in getattr(base, "__fields__", {}).items():
                fields[column] = type_
        for column, type_ in attrs.items():
            if isinstance(type_, Type):
                fields[column] = type_
            elif isinstance(type_, type) and issubclass(type_, Type):
                fields[column] = type_()
        attrs["__fields__"] = fields
        return type.__new__(cls, name, bases, attrs)


class Schema(Type, metaclass=_MapMetaclass):
    errors = {
        "type": "{name} 字段类型错误 请输入字典",
    }

    def __init__(
        self,
        keep_unknown: bool = False,
        nullable: bool = False,
        default: dict = None,
        description: str = None,
        data_from: str = None,
    ):
        super(Schema, self).__init__(
            nullable=nullable,
            default=default,
            description=description,
            data_from=data_from,
        )
        self.keep_unknown = keep_unknown

    def __call__(self, value: typing.Any, name: str = "") -> typing.Optional[dict]:
        if self.default is not None and value is None:
            return self.default
        if self.nullable and value is None:
            return value
        if not isinstance(value, dict):
            raise RequestInvalid(self.errors["type"].format(name=name))
        value = {**value}
        data = AttrDict()
        for column, type_ in getattr(self, "__fields__", {}).items():
            v = type_(
                value=value.pop(column, None),
                name=f"{name}.{column}" if name else f"{column}",
            )
            if getattr(type_, "nullable", False) and v is None:
                continue
            data[column] = v
        if self.keep_unknown:
            data.update(value)
        return data

    def get_schema(self) -> dict:
        extra = []
        if self.keep_unknown:
            extra.append("保留未知字段")
        return dict(
            type="object",
            type_class=self.__class__.__name__,
            properties={
                name: tp.get_schema()
                for name, tp in getattr(self, "__fields__", {}).items()
            },
            data_from=self.data_from,
            nullable=self.nullable,
            description=self.description,
            extra=", ".join(extra),
            default=self.default,
        )


class EmptyMap(Map):
    pass


def pagination(page: int, size: int, total: int) -> dict:
    """
    :param page: 当前页码
    :param size: 分页大小
    :param total: 元素总量
    """
    pages = total // size if size > 0 else 1
    return dict(page=page, total_pages=pages, total_results=total)


class PaginationResponse(Map):
    def __init__(self, items: List):
        super(PaginationResponse, self).__init__(
            {
                "results": items,
                "page": Integer(description="页码"),
                "total_pages": Integer(description="总页码"),
                "total_results": Integer(description="总记录数"),
            },
            description=items.description,
        )


class SingleResponse(Map):
    def __init__(self, data: Type):
        super(SingleResponse, self).__init__(
            {"data": data}, description=data.description
        )


class AttrDict(dict):
    def __getattr__(self, item):
        return self[item]
