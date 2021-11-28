from typing import Dict
from opentelemetry.trace import Span

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor


class HeliosUrllib3Instrumentor(HeliosBaseHttpInstrumentor):

    MODULE_NAME = 'opentelemetry.instrumentation.urllib3'
    INSTRUMENTOR_NAME = 'URLLib3Instrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider, response_hook=self.response_hook,
                                           request_hook=self.request_hook)

    @staticmethod
    def request_hook(span: Span, connection_pool, headers: Dict, body: str) -> None:
        HeliosUrllib3Instrumentor.base_request_hook(span, headers, body)

    @staticmethod
    def response_hook(span: Span, connection_pool, response) -> None:
        # connection_pool is an object of type urllib3.connectionpool.HTTPConnectionPool
        # response is an object of type urllib3.response.HTTPResponse

        response_headers = response.getheaders()
        response_payload = response.data
        HeliosUrllib3Instrumentor.base_response_hook(span, response_headers, response_payload)
