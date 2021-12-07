import ray

from .utilities import *
from .bus import *
from .elements import *


class PipelineModule:
    # @match_typing
    def __init__(self,
                 sources: List[EventSource] = None,
                 sinks: Dict[EventSink, List[Type]] = None,
                 analyzers: Dict[EventAnalyzer, List[Type]] = None,
                 other_generators: List[EventGenerator] = None,
                 other_listeners: Dict[EventListener, List[Type]] = None,
                 source_triggerers_thread_count = 1,
                 ray_config=None  # TODO determine ray config type
                 ):
        self.sources: List[EventSource] = get_not_none(sources, [])
        self.sinks: Dict[EventSink, List[Type]] = get_not_none(sinks, {})
        self.analyzers: Dict[EventAnalyzer, List[Type]] = get_not_none(analyzers, {})
        self.other_generators: List[EventGenerator] = get_not_none(other_generators, [])
        self.other_listeners: Dict[EventListener, List[Type]] = get_not_none(other_listeners, {})

        self.event_listeners: Dict[EventListener, List[Type]] = {**self.other_listeners, **self.sinks, **self.analyzers}
        self.event_generators: List[EventGenerator] = self.other_generators + self.sources + list(self.analyzers.keys())

        self.bus: EventBus = EventBus()
        for generator in self.event_generators:
            generator.event_handler = self.bus
        for listener in self.event_listeners:
            for t in self.event_listeners[listener]:
                self.bus.add_listener(listener, t)

        self.source_triggerers_thread_count = source_triggerers_thread_count

        self.use_ray = (ray_config is not None)
        self.ray_config = ray_config
        if self.use_ray:
            # ray.init(address='ray://192.168.242.92:31001')  # server
            ray.init(address='ray://192.168.243.216:10001')  # banaei

    def start(self):
        if self.use_ray:
            ray.get(start_pipeline_module_with_ray.remote(self))
        else:
            self.start_directly()

    def start_directly(self):
        for generator in self.event_generators:
            if isinstance(generator, TriggererEventSource):
                generator.start_generating()

    def stop(self):
        for generator in self.event_generators:
            if isinstance(generator, TriggererEventSource):
                generator.stop_generating()


@ray.remote
def start_pipeline_module_with_ray(pipeline_module: PipelineModule):
    pipeline_module.start_directly()
