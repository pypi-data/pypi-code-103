# -*- coding: utf-8 -*-
# @File    : router.py
# @Time    : 2021/11/26 4:24 下午


# -*- coding: utf-8 -*-
import base64
import functools
import inspect
import typing
from typing import Any
from typing import Callable
from typing import List

from flask import Blueprint
from flask import request, Request
from flask import Response

from basic_sdk import model
from basic_sdk import schema
from basic_sdk.func import integer
from basic_sdk.http import json_response

request: Request = request


class SchemaValidator(object):
    def __init__(self, name: str, _type: schema.Type):
        self.name = name
        self._type = _type
        self.data_from = schema.DATA(self._type.data_from)

    def __call__(self):
        if self.data_from == schema.DATA.JSON:
            if isinstance(self._type, (schema.Schema, schema.Map)):
                return self._type(value=schema.JSON(request.data))
            if isinstance(self._type, schema.List):
                return self._type(value=schema.LIST(request.data))
            data = schema.JSON(request.data)
            return self._type(value=data.get(self.name))
        if self.data_from == schema.DATA.PATH:
            paths: dict = request.view_args
            if isinstance(self._type, (schema.Schema, schema.Map)):
                return self._type(value=paths)
            return self._type(value=paths.get(self.name), name=self.name)
        if self.data_from == schema.DATA.QUERY:
            if isinstance(self._type, (schema.Schema, schema.Map)):
                return self._type(value=request.args.to_dict())
            if isinstance(self._type, schema.List):
                return self._type(value=request.args.getlist(self.name), name=self.name)
            return self._type(value=request.args.get(self.name), name=self.name)
        if self.data_from == schema.DATA.HEADER:
            if isinstance(self._type, (schema.Schema, schema.Map)):
                return self._type(value=dict(request.headers))
            return self._type(value=request.headers.get(self.name), name=self.name)
        if self.data_from == schema.DATA.COOKIE:
            if isinstance(self._type, (schema.Schema, schema.Map)):
                return self._type(value=dict(request.cookies))
            return self._type(value=request.cookies.get(self.name), name=self.name)
        if self.data_from == schema.DATA.FORM:
            if isinstance(self._type, schema.File):
                return self._type(value=request.files.get(self.name), name=self.name)
            if isinstance(self._type, schema.List) and isinstance(
                self._type.column, schema.File
            ):
                return self._type(
                    value=request.files.getlist(self.name), name=self.name
                )
            if isinstance(self._type, (schema.Schema, schema.Map)):
                return self._type(value=dict(request.form))
            return self._type(value=request.form.get(self.name), name=self.name)


class ModelValidator(object):
    def __init__(self, name: str, _type: Any, source: model.Source):
        self.name = name
        self._type = _type
        self.source = source
        self.data_from = self.source.data_from
        assert self.data_from in (
            "PATH",
            "QUERY",
            "HEADER",
            "COOKIE",
            "FORM",
            "FILE",
            "JSON",
        )
        self.alias = self.source.alias or self.name

    def __call__(self):
        if self.data_from == "PATH":
            paths = request.view_args or {}
            if self.source.embed or not model.is_dict_type(self._type):
                return model.validate(
                    value=paths.get(self.alias),
                    name=self.name,
                    source=self.source,
                    _type=self._type,
                    loc=("path", self.alias),
                )
            return model.validate(
                value=paths,
                name=self.name,
                source=self.source,
                _type=self._type,
                loc=("path",),
            )
        if self.data_from == "QUERY":
            if self.source.embed or not model.is_dict_type(self._type):
                if model.is_list_type(self._type):
                    return model.validate(
                        value=request.args.getlist(self.alias),
                        name=self.name,
                        source=self.source,
                        _type=self._type,
                        loc=("query", self.alias),
                    )
                return model.validate(
                    value=request.args.get(self.alias),
                    name=self.name,
                    source=self.source,
                    _type=self._type,
                    loc=("query", self.alias),
                )
            data = request.args.to_dict()
            if isinstance(self._type, type) and issubclass(self._type, model.Model):
                for name, _type in self._type.__fields__.items():
                    name = _type.alias or _type.name or name
                    if model.is_list_type(_type.outer_type_):
                        data[name] = request.args.getlist(name)
            return model.validate(
                value=data,
                name=self.name,
                source=self.source,
                _type=self._type,
                loc=("query",),
            )
        if self.data_from == "HEADER":
            if self.source.embed or not model.is_dict_type(self._type):
                if model.is_list_type(self._type):
                    return model.validate(
                        value=request.headers.getlist(self.alias),
                        name=self.name,
                        source=self.source,
                        _type=self._type,
                        loc=("header", self.alias),
                    )
                return model.validate(
                    value=request.headers.get(self.alias),
                    name=self.name,
                    source=self.source,
                    _type=self._type,
                    loc=("header", self.alias),
                )
            return model.validate(
                value=dict(request.headers),
                name=self.name,
                source=self.source,
                _type=self._type,
                loc=("header",),
            )
        if self.data_from == "COOKIE":
            if self.source.embed or not model.is_dict_type(self._type):
                return model.validate(
                    value=request.cookies.get(self.alias),
                    name=self.name,
                    source=self.source,
                    _type=self._type,
                    loc=("cookie", self.alias),
                )
            return model.validate(
                value=dict(request.cookies),
                name=self.name,
                source=self.source,
                _type=self._type,
                loc=("cookie",),
            )
        if self.data_from == "FORM":
            if self.source.embed or not model.is_dict_type(self._type):
                if model.is_list_type(self._type):
                    return model.validate(
                        value=request.form.getlist(self.alias),
                        name=self.name,
                        source=self.source,
                        _type=self._type,
                        loc=("form", self.alias),
                    )
                return model.validate(
                    value=request.form.get(self.alias),
                    name=self.name,
                    source=self.source,
                    _type=self._type,
                    loc=("form", self.alias),
                )
            data = dict(request.form)
            if isinstance(self._type, type) and issubclass(self._type, model.Model):
                for name, _type in self._type.__fields__.items():
                    name = _type.alias or _type.name or name
                    if model.is_list_type(_type.outer_type_):
                        data[name] = request.form.getlist(name)
            return model.validate(
                value=data,
                name=self.name,
                source=self.source,
                _type=self._type,
                loc=("form",),
            )
        if self.data_from == "FILE":
            if self.source.embed or not model.is_dict_type(self._type):
                if model.is_list_type(self._type):
                    return model.validate(
                        value=request.files.getlist(self.alias),
                        name=self.name,
                        source=self.source,
                        _type=self._type,
                        loc=("form", self.alias),
                    )
                return model.validate(
                    value=request.files.get(self.alias),
                    name=self.name,
                    source=self.source,
                    _type=self._type,
                    loc=("form",),
                )
            data = dict(request.files)
            if isinstance(self._type, type) and issubclass(self._type, model.Model):
                for name, _type in self._type.__fields__.items():
                    name = _type.alias or _type.name or name
                    if model.is_list_type(_type.outer_type_):
                        data[name] = request.files.getlist(name)
            return model.validate(
                value=data,
                name=self.name,
                source=self.source,
                _type=self._type,
                loc=("form",),
            )
        if self.data_from == "JSON":
            if self.source.embed:
                data = schema.JSON(request.data)
                if model.is_list_type(self._type):
                    return model.validate(
                        value=data.get(self.alias),
                        name=self.name,
                        source=self.source,
                        _type=self._type,
                        loc=("body", self.alias),
                    )
                return model.validate(
                    value=data.get(self.alias),
                    name=self.name,
                    source=self.source,
                    _type=self._type,
                    loc=("body",),
                )
            if model.is_list_type(self._type):
                return model.validate(
                    value=schema.LIST(request.data),
                    name=self.name,
                    source=self.source,
                    _type=self._type,
                    loc=("body", self.alias),
                )
            return model.validate(
                value=schema.JSON(request.data),
                name=self.name,
                source=self.source,
                _type=self._type,
                loc=("body",),
            )


class Router(object):
    OPTION_NAME = "_route_option"
    PREFIX_NAME = "_route_prefix"
    PUBLIC_SCHEMAS = "_route_public"
    PUBLIC_SCHEMA_VALIDATORS = "_router_public_validators"
    ROUTER_FUNCS = "_route_funcs"
    MIDDLEWARES = "_route_middlewares"
    RESPONSE_SCHEMAS = "_route_response_schemas"

    class Option(object):
        def __init__(self, method: str, rule: str, endpoint: str, description: str):
            self.method = method
            self.rule = rule.lstrip("/")
            self.endpoint = endpoint
            self.description = description

    class Prefix(object):
        def __init__(self, prefix: str, description: str):
            self.prefix = prefix.lstrip("/")
            self.description = description

    @classmethod
    def route(
        cls, method: str, rule: str, endpoint: str = None, description: str = None
    ):
        def decorator(func):
            funcs: set = getattr(cls, Router.ROUTER_FUNCS, set())
            if func.__qualname__ in funcs:
                raise RuntimeError(f"router func {func.__qualname__} already declared")
            funcs.add(func.__qualname__)
            setattr(cls, Router.ROUTER_FUNCS, funcs)

            option: Router.Option = Router.Option(
                method=method,
                rule=rule,
                endpoint=endpoint or func.__name__,
                description=description,
            )

            signature = inspect.signature(func)
            validators = []

            for name, param in signature.parameters.items():
                if isinstance(param.annotation, schema.Type):
                    validators.append(
                        SchemaValidator(name=name, _type=param.annotation)
                    )
                elif isinstance(param.default, model.Source):
                    validators.append(
                        ModelValidator(
                            name=name, _type=param.annotation, source=param.default
                        )
                    )
                elif name == "self":
                    continue
                else:
                    raise RuntimeError("parameter type undefined")

            @functools.wraps(func)
            def inner(self, **paths):
                public_validators: List[SchemaValidator] = getattr(
                    self, Router.PUBLIC_SCHEMA_VALIDATORS, []
                )
                middlewares: List[Callable[["BaseResource"], None]] = getattr(
                    self, Router.MIDDLEWARES, []
                )

                for validator in public_validators:
                    validator()

                data = {}
                for validator in validators:
                    data[validator.name] = validator()

                for middleware in middlewares:
                    middleware(self)

                response = func(self, **data)
                if isinstance(response, Response):
                    return response
                if isinstance(response, model.BaseModel):
                    return json_response(response.dict())
                return json_response(response)

            setattr(inner, Router.OPTION_NAME, option)
            return inner

        return decorator

    @classmethod
    def get(cls, rule: str, endpoint: str = None, description: str = None):
        return cls.route("GET", rule=rule, endpoint=endpoint, description=description)

    @classmethod
    def post(cls, rule: str, endpoint: str = None, description: str = None):
        return cls.route("POST", rule=rule, endpoint=endpoint, description=description)

    @classmethod
    def put(cls, rule: str, endpoint: str = None, description: str = None):
        return cls.route("PUT", rule=rule, endpoint=endpoint, description=description)

    @classmethod
    def delete(cls, rule: str, endpoint: str = None, description: str = None):
        return cls.route(
            "DELETE", rule=rule, endpoint=endpoint, description=description
        )

    @classmethod
    def prefix(cls, prefix: str, description: str):
        def decorator(class_cls):
            setattr(
                class_cls,
                Router.PREFIX_NAME,
                Router.Prefix(prefix=prefix, description=description),
            )
            return class_cls

        return decorator

    @classmethod
    def public(cls, **schemas: schema.Type):
        for name, _type in schemas.items():
            if not isinstance(_type, schema.Type):
                raise RuntimeError(f"parameter {name} type invalid.")

        schema_validators = [
            SchemaValidator(name, _type) for name, _type in schemas.items()
        ]

        def decorator(class_cls):
            setattr(class_cls, Router.PUBLIC_SCHEMA_VALIDATORS, schema_validators)
            setattr(class_cls, Router.PUBLIC_SCHEMAS, schemas)
            return class_cls

        return decorator

    @classmethod
    def middleware(cls, func: Callable[["BaseResource"], None]):
        def decorator(class_cls):
            middlewares: list = getattr(class_cls, Router.MIDDLEWARES, [])
            middlewares.append(func)
            setattr(class_cls, Router.MIDDLEWARES, middlewares)
            return class_cls

        return decorator

    @classmethod
    def response(
        cls, model_schema: typing.Type[model.Model], description: str, status: int = 200
    ):
        def decorator(func):
            response_schemas: list = getattr(func, Router.RESPONSE_SCHEMAS, [])
            response_schemas.append((status, description, model_schema))
            setattr(func, Router.RESPONSE_SCHEMAS, response_schemas)
            return func

        return decorator


class ResourceMetaclass(type):
    def __new__(cls, name, bases, attrs):
        routes = {}
        for func_name, value in attrs.items():
            option = getattr(value, Router.OPTION_NAME, None)
            if option and isinstance(option, Router.Option):
                routes[func_name] = value
        attrs["__routes__"] = routes
        return type.__new__(cls, name, bases, attrs)


class BaseResource(metaclass=ResourceMetaclass):
    @classmethod
    def json_response(cls, data: dict, status_code: int = 200, headers: dict = None):
        return json_response(data=data, status=status_code, headers=headers)

    @classmethod
    def pagination_response(
        cls, items: list, pagination: dict, status_code: int = 200, headers: dict = None
    ):
        return json_response(
            dict(
                results=items,
                page=pagination["page"],
                total_pages=pagination["total_pages"],
                total_results=pagination["total_results"],
            ),
            status=status_code,
            headers=headers,
        )

    @classmethod
    def request_params(cls) -> dict:
        params: dict = request.args.to_dict()
        return params

    @classmethod
    def request_cookies(cls):
        return request.cookies

    @classmethod
    def request_headers(cls):
        return request.headers

    @classmethod
    def request_json(cls) -> dict:
        return schema.JSON(request.data)

    @classmethod
    def request_content(cls) -> bytes:
        return request.data

    @classmethod
    def request_form(cls) -> dict:
        return dict(request.form)

    def __str__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}"


class BaseBlueprint(Blueprint):
    def __init__(self, name, import_name: str):
        super(BaseBlueprint, self).__init__(name=name, import_name=import_name)
        self._route_rules = {}
        self._groups = {}

    def add_url_rule(
        self, rule, endpoint=None, view_func=None, methods=None, **options
    ):
        rule_identifier = rule, ", ".join(methods or [])
        if rule_identifier in self._route_rules:
            previous = self._route_rules[rule_identifier]
            raise RuntimeError(
                f"route {methods} {rule} already declared. previous={previous}, redeclare at {endpoint}"
            )
        self._route_rules[rule_identifier] = endpoint
        return super(BaseBlueprint, self).add_url_rule(
            rule=rule,
            endpoint=endpoint,
            view_func=view_func,
            methods=methods,
            **options,
        )

    def register_resource(self, resource: BaseResource):
        resource_name = resource.__class__.__name__
        prefix: Router.Prefix = getattr(resource, Router.PREFIX_NAME, None)
        if prefix.description in self._groups:
            previous = self._groups[prefix.description]
            raise RuntimeError(
                f"Resource Group {prefix.description} already declared. "
                f"previous={previous}, redeclare at {resource}"
            )
        self._groups[prefix.description] = resource

        for name in getattr(resource, "__routes__").keys():
            func = getattr(resource, name, None)
            option: Router.Option = getattr(func, Router.OPTION_NAME, None)

            method: str = option.method
            endpoint: str = f"{resource_name}:{option.endpoint}"
            rule: str = option.rule
            if prefix and prefix.prefix:
                rule = f"/{prefix.prefix}/{rule}" if rule else f"/{prefix.prefix}"

            self.add_url_rule(
                rule=rule, endpoint=endpoint, view_func=func, methods=[method]
            )
