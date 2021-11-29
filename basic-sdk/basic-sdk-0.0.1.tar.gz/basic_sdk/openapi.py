# -*- coding: utf-8 -*-
# @File    : openapi.py
# @Time    : 2021/11/26 4:23 下午

import enum
import inspect
import re
import typing
from collections import defaultdict
from collections import OrderedDict
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple

import orjson
from flask import Flask
from flask import render_template_string
from flask import request
from werkzeug.routing import Rule

from basic_sdk.router import BaseResource
from basic_sdk.router import Router
from basic_sdk import model
from basic_sdk import schema


_SWAGGER_UI = """
<!DOCTYPE html>
<html>
<head>
<link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css">
<title>{{ app_name }} Api Docs</title>
<style type="text/css">
.renderedMarkdown {
    display: inline-block;
    padding-right: 8px;
}
.swagger-ui .renderedMarkdown p {
    margin: 0;
}
.swagger-ui .parameters-col_description input[type=text],
.swagger-ui .parameters-col_description select {
    display: block
}
tr.property-row {
    line-height: 20px;
}
tr.property-row:hover {
    background: #f8f8f8;
}
.swagger-ui .model {
    padding: 0 12px;
}
.property-row >td>.model>.prop>.property.primitive {
    padding: 0 3px;
}
.property-row >td>.model>.prop>.property.primitive>br {
    display: none;
}
.swagger-ui .parameter__name.required:after {
    content: ''
}
.swagger-ui .parameters-col_description .json-schema-form-item input[type=text] {
    display: inline-block;
}
.swagger-ui .parameters-col_description .json-schema-form-item>.json-schema-form-item-remove {
    display: inline-block;
    margin-left: 8px;
}
</style>
</head>
<body>
<div id="swagger-ui">
</div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
<!-- `SwaggerUIBundle` is now available on the page -->
<script>
const ui = SwaggerUIBundle({
    url: '/api/docs/openapi.json?swagger',
    dom_id: '#swagger-ui',
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
    ],
    layout: "BaseLayout",
    deepLinking: true,
    showExtensions: true,
    jsonEditor: true,
    sorter: "alpha",
    tagsSorter: "alpha",
    apisSorter: "alpha",
    showCommonExtensions: true,
    docExpansion: "none"
})
</script>
</body>
</html>
""".strip()

_RE_DOCS_UI = """
<!DOCTYPE html>
<html>
  <head>
    <title>{{ app_name }} Api Docs</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">

    <!--
    ReDoc doesn't change outer page styles
    -->
    <style>
      body {
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <redoc spec-url='/api/docs/openapi.json' sort-props-alphabetically></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>
  </body>
</html>
"""


class OpenApi(object):
    REF_PREFIX = "#/components/schemas/"
    RE_PATH_PARAMETERS = re.compile(r"<([^<>:]*:)?([^<>:]+)>")

    def __init__(self, app: Flask = None):
        self.app = app
        if app:
            self.init_app(app)
        self._schemas = OrderedDict()
        self._models = set()
        self._models_map = OrderedDict()

    def docs(self):
        app_name = (self.app.config.get("APP_NAME") or "").upper()
        if "swagger" in request.args:
            return render_template_string(_SWAGGER_UI, app_name=app_name)
        return render_template_string(_RE_DOCS_UI, app_name=app_name)

    def openapi(self):
        app_name = (self.app.config.get("APP_NAME") or "").upper()
        api = self._openapi()
        if "swagger" in request.args:
            api["info"] = {
                "title": f"{app_name} 接口文档",
                "description": "标准文档，请前往[文档](/api/docs)",
                "x-logo": {"url": "http://cdn.aizao.com/logo/logo.svg"},
            }
        else:
            api["info"] = {
                "title": f"{app_name} 接口文档",
                "description": "接口测试，请前往[文档](/api/docs?swagger)",
                "x-logo": {"url": "http://cdn.aizao.com/logo/logo.svg"},
            }
        return orjson.dumps(api, option=orjson.OPT_INDENT_2)

    def init_app(self, app: Flask):
        self.app = app

    def _openapi(self):
        if not getattr(self, "_cache_openapi", None):
            self._init_models()

            setattr(
                self,
                "_cache_openapi",
                {
                    "openapi": "3.0.2",
                    "info": {},
                    "tags": self._get_tags(),
                    "paths": self._get_paths(),
                    "components": self._get_components(),
                    "security": [{"basic_auth": []}],
                },
            )
        return getattr(self, "_cache_openapi")

    def _init_models(self):
        models = set()
        _models_map = {}

        for rule in self._iter_rules():
            func = self.app.view_functions[rule.endpoint]
            signature = inspect.signature(func)
            for name, param in signature.parameters.items():
                if isinstance(param.default, model.Source):
                    models |= model.get_models(
                        name=name, source=param.default, _type=param.annotation
                    )
            if isinstance(signature.return_annotation, type) and issubclass(
                signature.return_annotation, model.BaseModel
            ):
                models |= model.get_models(
                    name="return",
                    source=model.Source(),
                    _type=signature.return_annotation,
                )
            response_schemas = getattr(func, Router.RESPONSE_SCHEMAS, [])
            for _, _, model_schema in response_schemas:
                models |= model.get_models(
                    name="return", source=model.Source(), _type=model_schema
                )

        self._models = models
        self._models_map = model.get_models_map(models)

    def _get_components(self) -> dict:
        components = {
            "securitySchemes": {"basic_auth": {"type": "http", "scheme": "basic"}},
            "schemas": {
                "InternalServerError": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "integer", "description": "错误编码"},
                        "error": {
                            "type": "string",
                            "description": "错误类型",
                        },
                        "message": {"type": "string", "description": "错误说明"},
                        "trace_id": {"type": "string", "description": "请求链路ID"},
                    },
                },
                "Unauthorized": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "integer", "description": "错误编码"},
                        "error": {
                            "type": "string",
                            "description": "错误类型",
                        },
                        "message": {"type": "string", "description": "错误说明"},
                        "trace_id": {"type": "string", "description": "请求链路ID"},
                    },
                },
                "PermissionDenied": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "integer", "description": "错误编码"},
                        "error": {
                            "type": "string",
                            "description": "错误类型",
                        },
                        "message": {"type": "string", "description": "错误说明"},
                        "trace_id": {"type": "string", "description": "请求链路ID"},
                    },
                },
                "RequestInvalid": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "integer", "description": "错误编码"},
                        "error": {
                            "type": "string",
                            "description": "错误类型",
                        },
                        "message": {"type": "string", "description": "错误说明"},
                        "trace_id": {"type": "string", "description": "请求链路ID"},
                    },
                },
            },
        }

        schemas = {}
        for _type, name in self._models_map.items():
            info, definitions, nested_models = model.model_type_schema(
                _type,
                by_alias=True,
                model_name_map=self._models_map,
                known_models={_type},
                ref_prefix=self.REF_PREFIX,
                ref_template=model.default_ref_template,
            )
            schemas.update(definitions)
            schemas[name] = info
        components["schemas"].update(schemas)
        return components

    def _get_tags(self):
        tags = []
        for resource in self._get_resources():
            prefix = getattr(resource, Router.PREFIX_NAME, None)
            tags.append(
                {
                    "description": resource.__class__.__name__,
                    "name": prefix.description
                    if prefix
                    else resource.__class__.__name__,
                }
            )
        tags.sort(key=lambda x: x["name"])
        return tags

    def _get_paths(self):
        paths = defaultdict(dict)

        for rule in self._iter_rules():
            path, rule_paths = self._get_rule_paths(rule)
            paths[path].update(rule_paths)

        return paths

    def _get_resources(self) -> Set[BaseResource]:
        resources = set()
        for func in self.app.view_functions.values():
            if hasattr(func, "__self__") and isinstance(func.__self__, BaseResource):
                resources.add(func.__self__)
        return resources

    def _iter_rules(self) -> List[Rule]:
        rules = list(self.app.url_map.iter_rules())
        rules.sort(key=lambda r: r.rule)
        return rules

    def _get_rule_permissions(self, rule: Rule) -> str:
        func = self.app.view_functions[rule.endpoint]
        authority = getattr(func, "_authority", None)
        if authority:
            return authority.description

    def _get_rule_paths(self, rule: Rule) -> Tuple[str, dict]:
        def sub(x):
            parameter_type, parameter_name = x.groups()
            return "{%s}" % parameter_name.strip()

        func = self.app.view_functions[rule.endpoint]
        resource = getattr(func, "__self__", None)
        option = getattr(func, Router.OPTION_NAME, None)
        if isinstance(resource, BaseResource):
            prefix = getattr(resource, Router.PREFIX_NAME, None)
            tags = [prefix.description] if prefix else [resource.__class__.__name__]
        else:
            tags = ["Others"]
        summary = option.description if isinstance(option, Router.Option) else ""

        path: str = self.RE_PATH_PARAMETERS.sub(sub, rule.rule)

        methods = [
            method for method in rule.methods if method not in {"OPTIONS", "HEAD"}
        ]
        methods.sort()
        paths = {}

        for method in methods:
            response_schema = self._get_response_schema(rule)
            parameters = self._get_rule_parameters(rule)
            permissions = self._get_rule_permissions(rule)
            request_body = self._get_rule_request_body(rule)
            data = {
                "tags": tags,
                "summary": summary,
                "operationId": rule.endpoint,
                "responses": {
                    "422": {
                        "description": "请求参数错误",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/RequestInvalid"
                                }
                            }
                        },
                    }
                },
            }
            if parameters:
                data["parameters"] = parameters
            if request_body:
                data["requestBody"] = request_body
            if response_schema:
                data["responses"].update(response_schema)

            if permissions:
                data["responses"].update(
                    {
                        "401": {
                            "description": "用户未登录！",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Unauthorized"
                                    }
                                }
                            },
                        },
                        "403": {
                            "description": f"禁止访问！你没有 {permissions}",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/PermissionDenied"
                                    }
                                }
                            },
                        },
                    }
                )
            paths[method.lower()] = data
        return path, paths

    @classmethod
    def _format_parameters(
        cls, json_schema: dict, name: str = None, data_from: str = None
    ):
        description = json_schema["description"] or ""
        if json_schema.get("extra"):
            extra = json_schema["extra"]
            description = f"{description} ({extra})"

        data = {
            "schema": {
                "type": json_schema["type"],
            },
            "description": description,
            "required": not json_schema.get("nullable"),
        }
        if json_schema.get("enum"):
            data["schema"]["enum"] = json_schema["enum"]
        if json_schema["type"] == "array":
            data["schema"]["items"] = cls._format_basic_type(json_schema["items"])
        if name:
            data["name"] = name
        if data_from:
            data["in"] = data_from.lower()
        if json_schema.get("default") is not None:
            data["default"] = json_schema["default"]
        return data

    def _get_rule_parameters(self, rule: Rule) -> list:
        func = self.app.view_functions[rule.endpoint]
        signature = inspect.signature(func)
        parameters = []
        required = []
        public_schemas = {}
        if hasattr(func, "__self__") and hasattr(func.__self__, Router.PUBLIC_SCHEMAS):
            public_schemas = getattr(func.__self__, Router.PUBLIC_SCHEMAS)

        for name, _type in public_schemas.items():
            if not isinstance(_type, schema.Type):
                continue
            if _type.data_from in {schema.DATA.JSON, schema.DATA.FORM}:
                continue
            json_schema = _type.get_schema()
            if not isinstance(_type, (schema.Schema, schema.Map)):
                parameters.append(
                    self._format_parameters(json_schema, name, _type.data_from)
                )
            elif isinstance(_type, (schema.Schema, schema.Map)):
                for key, value in json_schema["properties"].items():
                    parameters.append(
                        self._format_parameters(value, key, _type.data_from)
                    )

        for name, param in signature.parameters.items():
            if not isinstance(param.annotation, schema.Type):
                continue
            _type = param.annotation
            if _type.data_from in {schema.DATA.JSON, schema.DATA.FORM}:
                continue
            json_schema = _type.get_schema()
            if not isinstance(_type, (schema.Schema, schema.Map)):
                parameters.append(
                    self._format_parameters(json_schema, name, _type.data_from)
                )
            elif isinstance(_type, (schema.Schema, schema.Map)):
                for key, value in json_schema["properties"].items():
                    parameters.append(
                        self._format_parameters(value, key, _type.data_from)
                    )
        for name, param in signature.parameters.items():
            if isinstance(param.annotation, schema.Type) or not isinstance(
                param.default, model.Source
            ):
                continue
            _type = param.annotation
            if param.default.data_from in ("JSON", "FORM", "FILE"):
                continue
            _schema = model.get_model_schema(
                name=name,
                model=_type,
                source=param.default,
                model_name_map=self._models_map,
                ref_prefix=self.REF_PREFIX,
            )
            if "properties" in _schema:
                for column, column_schema in _schema["properties"].items():
                    parameters.append(
                        {
                            "name": column,
                            "in": param.default.data_from.lower(),
                            "schema": column_schema,
                            "description": column_schema.get("description") or "",
                            "required": column in _schema.get("required", []),
                        }
                    )
            else:
                parameters.append(
                    {
                        "name": param.default.alias or name,
                        "in": param.default.data_from.lower(),
                        "schema": _schema,
                        "description": _schema.get("description") or "",
                        "required": param.default.required,
                    }
                )
        return parameters

    def _get_rule_request_body(self, rule: Rule) -> {}:
        func = self.app.view_functions[rule.endpoint]
        signature = inspect.signature(func)

        schemas: List[Tuple[str, typing.Any]] = []
        request_type = ""
        for name, param in signature.parameters.items():
            if isinstance(param.annotation, schema.Type):
                _type = param.annotation
                if _type.data_from == "JSON":
                    if request_type == "FORM":
                        raise RuntimeError("请求参数来源 data_from 不能同时包含 Form 和 JSON")
                    request_type = "JSON"
                    schemas.append((name, _type))
                if _type.data_from == "FORM":
                    if request_type == "JSON":
                        raise RuntimeError("请求参数来源 data_from 不能同时包含 Form 和 JSON")
                    request_type = "FORM"
                    schemas.append((name, _type))
            if isinstance(param.default, model.Source):
                if param.default.data_from == "JSON":
                    if request_type == "FORM":
                        raise RuntimeError("请求参数来源 data_from 不能同时包含 Form 和 JSON")
                    request_type = "JSON"
                    _schema = model.get_model_schema(
                        name=name,
                        model=param.annotation,
                        source=param.default,
                        model_name_map=self._models_map,
                        ref_prefix=self.REF_PREFIX,
                    )
                    if param.default.embed:
                        _schema = {
                            "type": "object",
                            "properties": {param.default.alias or name: _schema},
                        }
                    schemas.append((name, _schema))
                if (
                    param.default.data_from == "FORM"
                    or param.default.data_from == "FILE"
                ):
                    if request_type == "JSON":
                        raise RuntimeError("请求参数来源 data_from 不能同时包含 Form 和 JSON")
                    request_type = "FORM"
                    _schema = model.get_model_schema(
                        name=name,
                        model=param.annotation,
                        source=param.default,
                        model_name_map=self._models_map,
                        ref_prefix=self.REF_PREFIX,
                    )
                    if param.default.embed:
                        if param.default.extra:
                            _schema.update(param.default.extra)
                        _schema = {
                            "type": "object",
                            "properties": {param.default.alias or name: _schema},
                        }
                    schemas.append((param.default.alias or name, _schema))
        if not schemas:
            return
        if len(schemas) == 1:
            name, _schema = schemas[0]
            if isinstance(_schema, schema.File) or (
                isinstance(_schema, schema.List)
                and isinstance(_schema.column, schema.File)
            ):
                request_schema = dict(
                    type="object",
                    properties={name: self._format_schema(_schema.get_schema())},
                )
            elif isinstance(_schema, schema.Type):
                request_schema = self._format_schema(_schema.get_schema())
            else:
                request_schema = _schema
        else:
            request_schema = dict(type="object", properties={})
            for name, _schema in schemas:
                if isinstance(_schema, schema.Type):
                    if isinstance(_schema, (schema.Map, schema.Schema)):
                        request_schema["properties"].update(
                            _schema.get_schema()["properties"]
                        )
                    else:
                        request_schema["properties"].update(
                            {name: self._format_schema(_schema.get_schema())}
                        )
                else:
                    if _schema.get("type") == "object":
                        request_schema["properties"].update(_schema["properties"])
                    else:
                        request_schema["properties"].update({name: _schema})

        if (
            isinstance(request_schema, dict)
            and "properties" in request_schema
            and isinstance(request_schema["properties"], dict)
        ):
            required = set(request_schema.get("required") or [])
            for name, item in request_schema["properties"].items():
                if (
                    isinstance(item, dict)
                    and item.get("required")
                    and name not in required
                ):
                    required.add(name)
            request_schema["required"] = list(required)

        if request_type == "JSON":
            return {"content": {"application/json": {"schema": request_schema}}}
        else:
            return {"content": {"multipart/form-data": {"schema": request_schema}}}

    @classmethod
    def _format_basic_type(
        cls, json_schema: dict, name: str = None, data_from: str = None
    ):
        description = json_schema["description"] or ""
        if json_schema.get("extra"):
            extra = json_schema["extra"]
            description = f"{description} ({extra})"

        data = {
            "type": json_schema["type"],
            "description": description,
            "required": not json_schema.get("nullable"),
        }
        if json_schema.get("enum"):
            data["enum"] = json_schema["enum"]
        if json_schema.get("format"):
            data["format"] = json_schema["format"]
        if json_schema["type"] == "double":
            data["type"] = "number"
            data["format"] = "double"
        if name:
            data["name"] = name
        if data_from:
            data["in"] = data_from.lower()
        if json_schema.get("default") is not None:
            data["default"] = json_schema["default"]
        return data

    def _format_schema(self, json_schema: dict):
        type_name = json_schema["type"]
        if type_name in {"boolean", "integer", "double", "string"}:
            return self._format_basic_type(json_schema=json_schema)
        if type_name == "array":
            data = dict(
                type=type_name,
                items=self._format_schema(json_schema=json_schema["items"]),
            )
            if json_schema.get("description"):
                data["description"] = json_schema["description"]
            return data
        if type_name == "object":
            data = dict(
                type=type_name,
                properties={
                    name: self._format_schema(value)
                    for name, value in json_schema["properties"].items()
                },
            )
            if json_schema.get("description"):
                data["description"] = json_schema["description"]
            return data

    def _get_success_response(self, rule: Rule) -> Tuple[str, dict]:
        func = self.app.view_functions[rule.endpoint]
        annotations = func.__annotations__

        _schema = annotations.get("return")
        if _schema and isinstance(_schema, schema.Type):
            return _schema.description, self._format_schema(_schema.get_schema())
        if _schema:
            return "", model.get_model_schema(
                name="return",
                model=_schema,
                source=None,
                model_name_map=self._models_map,
                ref_prefix=self.REF_PREFIX,
            )
        return "", {}

    def _get_response_schema(self, rule: Rule) -> Dict:
        response_schema = {}
        func = self.app.view_functions[rule.endpoint]
        signature = inspect.signature(func)
        if signature.return_annotation is not inspect.Signature.empty:
            if isinstance(signature.return_annotation, schema.Type):
                response_schema["200"] = {
                    "description": signature.return_annotation.description,
                    "content": {
                        "application/json": {
                            "schema": self._format_schema(
                                signature.return_annotation.get_schema()
                            )
                        }
                    },
                }
            else:
                response_schema["200"] = {
                    "description": "",
                    "content": {
                        "application/json": {
                            "schema": model.get_model_schema(
                                name="return",
                                model=signature.return_annotation,
                                source=None,
                                model_name_map=self._models_map,
                                ref_prefix=self.REF_PREFIX,
                            )
                        }
                    },
                }
        response_schemas = getattr(func, Router.RESPONSE_SCHEMAS, [])
        for status, description, model_schema in response_schemas:
            response_schema[str(status)] = {
                "description": description,
                "content": {
                    "application/json": {
                        "schema": model.get_model_schema(
                            name="return",
                            model=model_schema,
                            source=None,
                            model_name_map=self._models_map,
                            ref_prefix=self.REF_PREFIX,
                        )
                    }
                },
            }
        return response_schema
