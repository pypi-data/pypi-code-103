from opentelemetry.trace import Span

from helios.instrumentation.base import HeliosBaseInstrumentor


class HeliosRedisInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.redis'
    INSTRUMENTOR_NAME = 'RedisInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider, response_hook=self.response_hook)

    def response_hook(self, span: Span, connection, response):
        if span and span.is_recording():
            if not hasattr(response, '__len__') or len(response) <= self.MAX_PAYLOAD_SIZE:
                span.set_attribute(self.DB_QUERY_RESULT_ATTRIBUTE_NAME, response)
