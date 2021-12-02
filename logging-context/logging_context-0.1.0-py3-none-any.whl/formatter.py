import logging


class LoggingContextFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "context"):
            record.context = None
        return super().format(record=record)

    def formatTime(self, record, datefmt=None):
        if not hasattr(record, "context"):
            record.context = None
        return super().formatTime(record=record, datefmt=datefmt)
