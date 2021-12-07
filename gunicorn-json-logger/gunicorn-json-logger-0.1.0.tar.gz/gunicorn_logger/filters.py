import logging

__all__ = (
    "add_access_log_filter",
    "HealthCheckFilter"
)

_access_loggers = ("gunicorn.access", "uvicorn.access")


def add_access_log_filter(filter_):
    for log_name in _access_loggers:
        logger = logging.getLogger(log_name)
        logger.addFilter(filter_)


class HealthCheckFilter(logging.Filter):
    def __init__(self, path, method="GET"):
        self.method = method
        self.path = path

        super().__init__()

    def filter(self, record):
        if self.path:
            return f"{self.method} {self.path}" not in record.getMessage()

        return True
