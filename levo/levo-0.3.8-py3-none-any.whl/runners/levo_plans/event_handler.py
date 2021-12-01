from typing import Dict, List

import attr
from levo_commons import events

from ...config import TestPlanCommandConfig
from ...handlers import EventHandler
from ...logger import get_logger
from .context import ExecutionContext
from .modules import Module, initialize_module

log = get_logger(__name__)


@attr.s()
class LevoPlansEventHandler(EventHandler):
    config: TestPlanCommandConfig = attr.ib()
    modules: Dict[str, Module] = attr.ib(factory=dict)
    reporters: List[EventHandler] = attr.ib(factory=list)

    def delegate_to_reporters(self, context, event):
        for reporter in self.reporters:
            reporter.handle_event(context, event)

    def setup_modules(self, module_names):
        for module_name in module_names:
            if module_name not in self.modules:
                module = initialize_module(module_name)
                module.setup(self.config)
                self.modules[module_name] = module

    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        if isinstance(event, events.BeforeTestSuiteExecution):
            if event.payload.modules:
                self.setup_modules(event.payload.modules)
        elif isinstance(event, events.BeforeTestCaseExecution):
            if event.payload.module:
                self.setup_modules([event.payload.module])
        elif (
            isinstance(event, events.Finished)
            or isinstance(event, events.Interrupted)
            or isinstance(event, events.InternalError)
        ):
            # Stop all the modules
            for module in self.modules.values():
                module.teardown()

        # Delegate all the events to the reporters too.
        self.delegate_to_reporters(context, event)
