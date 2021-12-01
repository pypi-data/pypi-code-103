"""
Instrumentation elements
"""
import time
from abc import ABC
from typing import Optional, Union, List, Dict

from jaeger_client import Config, Span, SpanContext, Tracer
from opentracing import Format
from opentracing.tracer import Reference
import opentracing
import apache_beam.transforms.core as beam_core


# pylint: disable=too-few-public-methods
class TracerConfig:
    """
    Configuration of TracerClass
    """
    def __init__(self, service_name: str, reporting_host: str, reporting_port: str):
        self.service_name = service_name
        self.reporting_host = reporting_host
        self.reporting_port = reporting_port


# pylint: disable=too-few-public-methods
class Singleton(type):
    """
    Singleton Class - enables to create singletons with with initialization arguments
    """
    instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


class TracerClass(metaclass=Singleton):
    """
    Used for Spans and Traces
    Note: There can only be one tracers, hence we need to make a singleton class
    """
    def __init__(self, config: TracerConfig):
        self.config = config

        local_agent = {}  # Default empty - if run on localhost
        if self.config.reporting_host != 'localhost':
            local_agent['reporting_host'] = self.config.reporting_host
            local_agent['reporting_port'] = self.config.reporting_port

        tracer_config = Config(
            config={
                'sampler': {
                    'type': 'const',
                    'param': 1,
                },
                'local_agent': local_agent,
                'logging': False,
            },
            service_name=self.config.service_name,
            validate=True,
        )

        tracer: Optional[Tracer] = tracer_config.initialize_tracer()
        if tracer is None:
            raise RuntimeError('Tracer was not initialized')
        self.tracer: Tracer = tracer

    def get_tracer(self) -> Optional[Tracer]:
        """
        Returns the tracer
        """
        return self.tracer

    # pylint: disable=too-many-arguments
    def start_span(self,
                   operation_name: Optional[str] = None,
                   child_of: Union[None, Span, SpanContext] = None,
                   references: Union[List[Reference], None, Reference] = None,
                   tags: Union[dict, None] = None,
                   start_time: Optional[float] = None,
                   ignore_active_span: bool = False,
                   ) -> Span:
        """
        Start and return a new Span representing a unit of work.

        :param operation_name: name of the operation represented by the new
            span from the perspective of the current service.
        :param child_of: shortcut for 'child_of' reference
        :param references: (optional) either a single Reference object or a
            list of Reference objects that identify one or more parent
            SpanContexts. (See the opentracing.Reference documentation for detail)
        :param tags: optional dictionary of Span Tags. The caller gives up
            ownership of that dictionary, because the Tracer may use it as-is
            to avoid extra data copying.
        :param start_time: an explicit Span start time as a unix timestamp per
            time.time()
        :param ignore_active_span: an explicit flag that ignores the current
            active :class:`Scope` and creates a root :class:`Span`

        :return: Returns an already-started Span instance.
        """
        return self.tracer.start_span(operation_name, child_of, references, tags, start_time, ignore_active_span)

    # pylint: disable=redefined-builtin
    def inject(self, span_context: Union[Span, SpanContext], format: str, carrier: dict):
        """
        Injects span to a carrier
        """
        self.tracer.inject(span_context, format, carrier)

    def get_carrier(self, span: Span) -> Dict:
        """
        Helper method to get a carrier from a span, which can be serialized.
        This method creates the context to SpansDoFn class
        """
        span_ctx: Dict = {}
        self.tracer.inject(span, format=Format.TEXT_MAP, carrier=span_ctx)
        carrier_ctx = {'span_ctx': span_ctx,
                       'service_name': self.config.service_name,
                       'reporting_host': self.config.reporting_host,
                       'reporting_port': self.config.reporting_port}
        return carrier_ctx

    # pylint: disable=redefined-builtin
    def extract(self, format: str, carrier: dict) -> SpanContext:
        """
        Extracts span from carrier
        """
        return self.tracer.extract(format, carrier)

    @staticmethod
    def close():
        """
        Call this function to ensure all spans are flushed to Jaeger
        """
        # Sleep needed to flush the spans from Jaeger_Client
        # yield to IOLoop to flush the spans - https://github.com/jaegertracing/jaeger-client-python/issues/50
        time.sleep(2)


class TracerDoFn(beam_core.DoFn, ABC):
    """
    Helper class to make Spans and Traces
    """
    # pylint: disable=too-many-arguments
    def __init__(self, do_fn: beam_core.DoFn,
                 carrier_ctx: Dict,
                 tag_index=None,
                 tag_name='tag'):
        super().__init__()

        self.do_fn = do_fn
        self.config = TracerConfig(carrier_ctx['service_name'],
                                   carrier_ctx['reporting_host'],
                                   carrier_ctx['reporting_port'])
        self.span_ctx = carrier_ctx['span_ctx']
        self.span = None
        self.tracer = None
        self.tag_index = tag_index
        self.tag_name = tag_name

    def setup(self):
        self.do_fn.setup()

    def start_bundle(self):
        self.do_fn.start_bundle()
        self.tracer = TracerClass(self.config)
        span_ctx_obj = self.tracer.extract(Format.TEXT_MAP, self.span_ctx)
        self.span = self.tracer.start_span(operation_name=self.do_fn.__class__.__name__,
                                           references=opentracing.child_of(span_ctx_obj))

    def finish_bundle(self):
        self.do_fn.finish_bundle()
        self.span.finish()
        # Sleep needed to flush the spans from Jaeger_Client
        # yield to IOLoop to flush the spans - https://github.com/jaegertracing/jaeger-client-python/issues/50
        time.sleep(2)

    def teardown(self):
        self.do_fn.teardown()

    def process(self, element, *args, **kwargs):
        with self.tracer.start_span(operation_name=f'{self.do_fn.__class__.__name__}-process',
                                    child_of=self.span) as span:
            if self.tag_index is not None:
                span.set_tag(self.tag_name, element[self.tag_index])
            return self.do_fn.process(element, *args, **kwargs)
