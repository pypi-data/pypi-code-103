from logging import getLogger, Formatter, StreamHandler, FATAL, INFO
from sys import stdout


_SUPPRESSED_NAMESPACES = ("boto3", "requests", "datadog")
_LOG_FORMAT = "%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s"
#  [%(pathname)s(L%(lineno)d):%(funcName)s]


def get_logger(level=INFO, suppressed_namespaces=_SUPPRESSED_NAMESPACES):
    """
    Create a configured root logger and suppress any namespaces specified

    Args:
        level (logging log level, optional): The Python logging library level you wish to log at. Defaults to INFO.
        suppressed_namespaces (set(str), optional): A set of namespaces to supporess logging for. Defaults to _SUPPRESSED_NAMESPACES.
    """

    # Retrieve and setup root namespace logger
    root_logger = getLogger()
    root_logger.setLevel(level)
    formatter = Formatter(fmt=_LOG_FORMAT)
    stdout_handler = StreamHandler(stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(level)
    root_logger.addHandler(stdout_handler)

    # Suppress supplied logging namespaces
    _suppress_logging_namespaces(suppressed_namespaces)

    return root_logger


def _suppress_logging_namespaces(namespaces):
    """Accepts a set of namespaces and sets the logging level such that they are effectively suppressed
    Args:
        namespaces (set(str)): a set of unique namespaces to suppress logging for
    """
    for namespace in namespaces:
        namespace_logger = getLogger(namespace)
        namespace_logger.setLevel(FATAL)
