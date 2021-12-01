import json
from typing import List, Dict, Optional, Union

import wrapt
from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor


class HeliosFastAPIInstrumentor(HeliosBaseHttpInstrumentor):

    MODULE_NAME = 'opentelemetry.instrumentation.fastapi'
    INSTRUMENTOR_NAME = 'FastAPIInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)
        self.tracer_provider = None
        self.instrumented_apps = set()

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return
        self.tracer_provider = tracer_provider
        wrapt.wrap_function_wrapper('fastapi', 'FastAPI.__init__', self.fastapi_instrument_and_init)

    def uninstrument(self):
        if self.get_instrumentor() is None:
            return

        for app in self.instrumented_apps:
            self.get_instrumentor().uninstrument_app(app)
        self.instrumented_apps = set()

    def fastapi_instrument_and_init(self, wrapped, instance, args, kwargs):
        init_response = wrapped(*args, **kwargs)
        if instance not in self.instrumented_apps:
            self.instrumented_apps.add(instance)
            self.get_instrumentor().instrument_app(instance, tracer_provider=self.tracer_provider)

            get_route_details = HeliosBaseHttpInstrumentor.import_attribute(self.MODULE_NAME, '_get_route_details')
            instance.add_middleware(HeliosMiddleware,
                                    tracer=self.tracer_provider.get_tracer(__name__),
                                    get_span_details=get_route_details)
        return init_response


class HeliosMiddleware:

    def __init__(self, app, tracer=None, get_span_details=None):
        self.app = app
        self.tracer = tracer
        self.get_span_details = get_span_details or self.get_default_span_details

    @staticmethod
    def get_default_span_details(scope: Dict):
        span_name = scope.get("path", "").strip() or "HTTP {}".format(
            scope.get("method", "").strip()
        )

        return span_name, {}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        span_name, attributes = self.get_span_details(scope)

        self.set_url(attributes, scope)

        request_headers = self.extract_headers(scope.get('headers'))
        attributes[HeliosBaseHttpInstrumentor.HTTP_REQUEST_HEADERS_ATTRIBUTE_NAME] = json.dumps(request_headers)

        with self.tracer.start_as_current_span(
            f"Helios fastapi {span_name}", kind=trace.SpanKind.SERVER,
        ) as span:
            span.set_attributes(attributes)

            async def wrapped_send(message):
                if 'headers' in message:
                    response_headers = HeliosMiddleware.extract_headers(message.get('headers'))
                    span.set_attribute(
                        HeliosBaseHttpInstrumentor.HTTP_RESPONSE_HEADERS_ATTRIBUTE_NAME,
                        json.dumps(response_headers))

                if 'body' in message:
                    span.set_attribute(
                        HeliosBaseHttpInstrumentor.HTTP_RESPONSE_BODY_ATTRIBUTE_NAME, message.get('body'))

                return await send(message)

            async def wrapped_receive():
                message = await receive()
                if 'body' in message:
                    span.set_attribute(
                        HeliosBaseHttpInstrumentor.HTTP_REQUEST_BODY_ATTRIBUTE_NAME, message.get('body'))
                return message

            return await self.app(scope, wrapped_receive, wrapped_send)

    @staticmethod
    def extract_headers(headers: Optional[List]) -> Optional[Dict]:
        if headers is None:
            return None
        return {
            HeliosMiddleware.bytes_to_str(key): HeliosMiddleware.bytes_to_str(value)
            for (key, value) in headers
        }

    @staticmethod
    def bytes_to_str(str_or_bytes: Union[str, bytes]) -> str:
        return str_or_bytes.decode() if isinstance(str_or_bytes, bytes) else str_or_bytes

    @staticmethod
    def set_url(attributes, scope):
        url = ''
        try:
            protocol = scope.get('type')
            host, port = scope.get('server')
            root_path = scope.get('root_path')
            path = scope.get('path')
            port = '' if port in [80, 443] else f':{port}'

            url = f'{protocol}://{host}{port}{root_path}{path}'
        finally:
            attributes[SpanAttributes.HTTP_URL] = url
