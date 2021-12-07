import json
from collections import OrderedDict
from typing import Any

import regex
import yaml
from pydantic import BaseModel

from kntgen.constants import *
from kntgen.str_helpers import *

DEFAULT_CONTENT_TYPE = 'String'
DEFAULT_CONTENT_TYPE_FILE = 'File'
REGEX_FIND_PATH = r'/{(.*?)}'
ENDPOINT_CONVERSION = {
    'get': '@GET',
    'post': '@POST',
    'patch': '@PATCH',
    'put': '@PUT',
    'delete': '@DELETE'
}
IMPORT_API_SERVICE_HEADER = """import 'package:dio/dio.dart' hide Headers;
import 'package:retrofit/http.dart';

import '../../model/network_models.dart';

part 'api_service.g.dart';
"""
IMPORT_CLOUD_REPO_HEADER = """import '../model/network_models.dart';

abstract class CloudRepo {
"""
IMPORT_CLOUD_REPO_FOOTER = """}
"""
IMPORT_DATA_CLOUD_REPO_HEADER = """import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';

import '../../../model/network_models.dart';
import '../../../repo/cloud_repo.dart';

@Singleton(as: CloudRepo)
class DataCloudRepo {"""
IMPORT_DATA_CLOUD_REPO_FOOTER = """
}

Future<Dio> _createDio({
  bool needAuthorized = false,
  Map<String, dynamic> customHeaders = const {},
}) async {
  final dio = Dio(BaseOptions(
    connectTimeout: _defaultConnectionTimeout,
    receiveTimeout: _defaultReceiveTimeout,
    headers: customHeaders,
  ));
  if (needAuthorized) {
    final token = '';
    dio.interceptors
        .add(InterceptorsWrapper(onRequest: (options, handlers) async {
      dio.lock();
      options.headers[HttpHeaders.authorizationHeader] = 'Bearer $token';
      options.headers[HttpHeaders.contentTypeHeader] =
      'application/json; charset=UTF-8';
      dio.unlock();
    }));
  }
  if (Flavors.debugMode) {
    dio.interceptors.add(PrettyDioLogger(
      request: true,
      requestHeader: true,
    ));
  }
  return dio;
}
"""


@auto_str
class Unit(BaseModel):
    title: str
    content: str = None
    content_type: str = DEFAULT_CONTENT_TYPE

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.content and is_number(self.content):
            self.content_type = 'num'

    @property
    def title_camel_case(self):
        just_letter = ''.join([c for c in self.title if c not in '-._'])
        return to_camel_case(just_letter)

    @property
    def is_file_type(self):
        return 'file' in self.content_type.lower()

    @property
    def is_list_type(self):
        return 'list' in self.content_type.lower()

    @property
    def is_optional(self):
        return self.content_type.endswith('?')

    @property
    def value(self):
        value = self.content
        if value and self.content_type.startswith('String'):
            value = f'{value!r}'
        return value

    @property
    def non_null_value(self):
        if self.content:
            value = self.content
        elif self.content_type in DART_TYPES_DEFAULT_VALUES:
            value = DART_TYPES_DEFAULT_VALUES[self.content_type]
        elif self.is_list_type:
            value = '[]'
        elif self.is_file_type:
            value = f'\'path_to_{self.title}\''
        else:
            value = f'{self.content_type}()'
        if self.content_type.startswith('String'):
            value = f'{value!r}'
        return value


@auto_str
class API(BaseModel):
    name: str
    method: str = 'get'
    endpoint: str
    request_type: str = None
    headers: list[Unit] = []
    queries: list[Unit] = []
    body: list[Unit] = []
    fields: list[Unit] = []
    parts: list[Unit] = []
    response_type: str = None
    response_json: str = '{}'

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Remove mistake if has
        if self.method == 'get':
            self.body = []
            self.fields = []
            self.parts = []

    @property
    def has_param(self):
        return len(self.path_from_endpoint) > 0 \
               or len(self.headers) > 0 \
               or len(self.queries) > 0 \
               or len(self.body) > 0 \
               or len(self.fields) > 0 \
               or len(self.parts) > 0

    @property
    def name_camel_case(self):
        return to_camel_case(self.name)

    @property
    def name_pascal_case(self):
        return to_pascal_case(self.name)

    @property
    def name_snake_case(self):
        return to_snake_case(self.name)

    @property
    def name_to_word(self):
        return to_words(self.name)

    @property
    def request_type_pascal_case(self):
        return to_pascal_case(self.request_type)

    @property
    def request_type_snake_case(self):
        return to_snake_case(self.request_type)

    @property
    def response_type_pascal_case(self):
        return to_pascal_case(self.response_type)

    @property
    def response_type_snake_case(self):
        return to_snake_case(self.response_type)

    @property
    def is_get_method(self):
        return self.method == 'get'

    @property
    def retrofit_endpoint(self):
        method_type = ENDPOINT_CONVERSION[self.method] or '@GET'
        return f'{method_type}({self.endpoint!r})'

    @property
    def static_headers(self):
        return [header for header in self.headers if header.content]

    @property
    def dynamic_headers(self):
        return [header for header in self.headers if not header.content]

    @property
    def path_from_endpoint(self):
        # Extract paths if needed
        paths = regex.findall(REGEX_FIND_PATH, self.endpoint)
        return {path: to_camel_case(path) for path in paths}

    @property
    def has_fields(self):
        return len(self.fields) > 0

    @property
    def has_file_part(self):
        for part in self.parts:
            if part.is_file_type:
                return True
        return False


@auto_str
class RestfulService(BaseModel):
    name: str
    base_url: str
    headers: list[Unit] = []
    apis: list[API] = []

    @classmethod
    def from_json(cls, json_str: str):
        json_model = json.loads(json_str)
        return cls(**json_model)

    @classmethod
    def from_yaml(cls, yaml_stream):
        yaml_model = yaml.safe_load(yaml_stream)
        return cls(**yaml_model)

    @property
    def name_camel_case(self):
        return to_camel_case(self.name)

    @property
    def name_pascal_case(self):
        return to_pascal_case(self.name)

    @property
    def name_snake_case(self):
        return to_snake_case(self.name)

    def to_dict(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__),
                          object_pairs_hook=OrderedDict)
