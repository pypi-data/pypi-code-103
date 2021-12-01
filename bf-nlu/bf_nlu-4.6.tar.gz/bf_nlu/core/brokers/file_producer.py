from bf_nlu.constants import DOCS_URL_EVENT_BROKERS
from bf_nlu.core.brokers.file import FileEventBroker
from bf_nlu.utils.common import raise_warning


class FileProducer(FileEventBroker):
    raise_warning(
        "The `FileProducer` class is deprecated, please inherit from "
        "`FileEventBroker` instead. `FileProducer` will be removed in "
        "future bf_nlu versions.",
        FutureWarning,
        docs=DOCS_URL_EVENT_BROKERS,
    )
