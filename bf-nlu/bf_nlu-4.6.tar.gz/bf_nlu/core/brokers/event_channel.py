from bf_nlu.core.brokers.broker import EventBroker


# noinspection PyAbstractClass
from bf_nlu.utils.common import raise_warning


class EventChannel(EventBroker):
    raise_warning(
        "The `EventChannel` class is deprecated, please inherit from "
        "`EventBroker` instead. `EventChannel` will be removed "
        "in future bf_nlu versions.",
        DeprecationWarning,
        stacklevel=2,
    )
