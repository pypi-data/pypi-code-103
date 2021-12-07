from enum import Enum

from kntgen.model.network import *
from kntgen.str_helpers import *

REQUIRED_FIELD = '**required**'


class HttpMethod(str, Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @property
    def value_lower_case(self):
        return self.value.lower()


class HttpBodyMode(str, Enum):
    RAW = 'raw'
    FORM_DATA = 'formdata'
    FORM_URL_ENCODED = 'urlencoded'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class HttpFormDataType(str, Enum):
    TEXT = 'text'
    FILE = 'file'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    def convert_to_network_form_data_type(self):
        return {
            HttpFormDataType.TEXT: DEFAULT_CONTENT_TYPE,
            HttpFormDataType.FILE: DEFAULT_CONTENT_TYPE_FILE
        }.get(self, DEFAULT_CONTENT_TYPE)


@auto_str
class PostmanUnit:
    def __init__(self, **kwargs):
        self.key = kwargs.get('key')
        self.value = kwargs.get('value')
        self.type_value = kwargs.get('type')
        self.type = HttpFormDataType(self.type_value) \
            if HttpFormDataType.has_value(
            self.type_value) else HttpFormDataType.TEXT
        self.source_file = kwargs.get('src')

    def __eq__(self, other):
        return isinstance(other, __class__) \
               and other.key == self.key \
               and other.value == self.value

    def __hash__(self):
        return id(f'{self.key}_{self.value}')

    def convert_to_network_unit(self):
        return Unit(
            title=self.key,
            content=self.value,
            content_type=self.type.convert_to_network_form_data_type()
        )


@auto_str
class PostmanApiRequestBody:
    def __init__(self, **kwargs):
        self.mode_value = kwargs.get('mode')
        self.mode = HttpBodyMode(self.mode_value) \
            if HttpBodyMode.has_value(self.mode_value) else None
        self.data = kwargs.get(self.mode_value)

    def convert_to_body_network_unit(self):
        if self.mode == HttpBodyMode.RAW:
            data_dict = json.loads(self.data or '{}',
                                   object_pairs_hook=OrderedDict)
            units = []
            return Unit(
                title=self.key,
                content=self.value
            )
        return []

    def convert_to_field_network_unit(self):
        return Unit(
            title=self.key,
            content=self.value
        )

    def convert_to_part_network_unit(self):
        return Unit(
            title=self.key,
            content=self.value
        )


@auto_str
class PostmanApiRequest:
    def __init__(self, **kwargs):
        self.method = HttpMethod(kwargs.get('method')) \
            if HttpMethod.has_value(kwargs.get('method')) else HttpMethod.GET
        self.url = kwargs.get('url', {})
        self.headers = [PostmanUnit(**v) for v in kwargs.get('header', [])]
        self.body = PostmanApiRequestBody(
            **kwargs['body']) if 'body' in kwargs else None
        self.protocol = self.url.get('protocol')
        self.hosts = self.url.get('host', [])
        self.paths = [f'{{{p[1:]}}}' if p.startswith(':') else p for p in
                      self.url.get('path', []) if p]
        self.queries = [PostmanUnit(**v) for v in self.url.get('query', [])]

    @property
    def host(self):
        if not self.hosts:
            return REQUIRED_FIELD
        protocol_present = f'{self.protocol}://' if self.protocol else ''
        return protocol_present + '/'.join(self.hosts)

    @property
    def endpoint(self):
        if not self.paths:
            return REQUIRED_FIELD
        return '/' + '/'.join(self.paths)

    def body(self):
        return self.body.convert_to_body_network_unit() if self.body else []

    def fields(self):
        return self.body.convert_to_field_network_unit() if self.body else []

    def parts(self):
        return self.body.convert_to_part_network_unit() if self.body else []


@auto_str
class PostmanApi:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.sample_api = kwargs.get('response', [])
        self.request = None
        if self.sample_api:
            self.request = PostmanApiRequest(
                **self.sample_api[0]['originalRequest']) \
                if 'originalRequest' in self.sample_api[0] else None
        self.response = {}

    @property
    def name_camel_case(self):
        return to_camel_case(self.name)

    @property
    def name_pascal_case(self):
        return to_pascal_case(self.name)

    def method(self):
        return self.request.method.value_lower_case \
            if self.request else HttpMethod.GET.value_lower_case

    def host(self):
        return self.request.host if self.request else REQUIRED_FIELD

    def endpoint(self):
        return self.request.endpoint if self.request else REQUIRED_FIELD

    def request_type(self):
        return f'{self.name_pascal_case}Request'

    def headers(self):
        return [header_unit.convert_to_network_unit() for header_unit in
                self.request.headers] if self.request else []

    def queries(self):
        return [query_unit.convert_to_network_unit() for query_unit in
                self.request.queries] if self.request else []

    def response_type(self):
        return f'{self.name_pascal_case}Response'


@auto_str
class PostmanEnvironmentUnit:
    def __init__(self, **kwargs):
        self.key = kwargs.get('key')
        self.value = kwargs.get('value')
        self.enabled = kwargs.get('enabled', True)


@auto_str
class PostmanEnvironment:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.units = [PostmanEnvironmentUnit(**v) for v in
                      kwargs.get('values', [])]


@auto_str
class PostmanCollection:
    def __init__(self, **kwargs):
        info = kwargs.get('info', dict())
        self.id = info.get('_postman_id')
        self.name = info.get('name')
        self.schema = info.get('schema')
        self.environment = PostmanEnvironment(**info.get('environment')) \
            if 'environment' in info else None
        # Recursive to find all API from sub folder
        raw_apis = []
        PostmanCollection.collect_raw_api(postman_item=kwargs.get('item', []),
                                          results=raw_apis)
        self.apis = [PostmanApi(**i) for i in raw_apis]

    @staticmethod
    def collect_raw_api(postman_item, results: list):
        if postman_item is None or results is None:
            return
        if isinstance(postman_item, list):
            for sub_item in postman_item:
                PostmanCollection.collect_raw_api(
                    postman_item=sub_item,
                    results=results)
            return
        if not isinstance(postman_item, dict):
            return
        if 'response' in postman_item:
            results.append(postman_item)
            return
        if 'item' in postman_item:
            PostmanCollection.collect_raw_api(
                postman_item=postman_item['item'],
                results=results)

    @property
    def common_host(self):
        # Get common host
        host = REQUIRED_FIELD
        if self.apis:
            existed_host_apis = [api for api in self.apis if
                                 api.host != REQUIRED_FIELD]
            if existed_host_apis:
                first_api_host = existed_host_apis[0].host
                for api in existed_host_apis[1:]:
                    if first_api_host != api.host:
                        return host
                host = first_api_host
        # Then replace with environment value if needed
        if self.environment:
            for unit in self.environment.units:
                if unit.enabled and unit.key in host:
                    host = unit.value
                    if not ''.startswith('https://'):
                        host = f'https://{host}'
                    break
        return host

    @property
    def common_headers(self):
        # Find all common headers
        headers = []
        if self.apis:
            existed_header_apis = [api for api in self.apis if
                                   api.request and api.request.headers]
            if len(existed_header_apis) != len(self.apis):
                # Guaranteed this case doesn't have common headers
                return headers

            headers = existed_header_apis[0].request.headers
            for api in existed_header_apis[1:]:
                headers = list(set(api.request.headers).intersection(headers))
        return headers

    def convert_to_restful_api_model(self):
        return RestfulService(
            name=self.name,
            base_url=self.common_host,
            headers=[header_unit.convert_to_network_unit() for header_unit in
                     self.common_headers],
            apis=[
                API(
                    name=api.name_camel_case,
                    method=api.method(),
                    endpoint=api.endpoint(),
                    request_type=api.request_type(),
                    headers=api.headers(),
                    response_type=api.response_type()
                ) for api in self.apis if api
            ]
        )
