"""Configure logging

"""
import logging
from logging.config import dictConfig
from pathlib import Path

##__________________________________________________________________||
_module_path = Path(__file__).resolve().parent.parent
# the path to the dir in which the module is installed,
# i.e., the one dir above the module path.
# e.g., /home/username/venv/lib/python3.8/site-packages

# https://docs.python.org/3/library/logging.html#logrecord-objects
_old_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs):
    """replace the pathname (the full pathname of the source file) with
    the relative path of the source file in the package

    For example, replace
    "/home/username/venv/lib/python3.8/site-packages/acondbs/schema/auth.py"
    with
    "acondbs/schema/auth.py"

    """

    record = _old_factory(*args, **kwargs)
    try:
        record.pathname = (
            Path(record.pathname).resolve().relative_to(_module_path)
        )
    except Exception:
        pass
    return record


logging.setLogRecordFactory(record_factory)


##__________________________________________________________________||
def configure_logging():
    """configure logging

    This function needs to be called early in the program, i.e., in
    the beginning of create_app() before app.logger is accessed. (It
    seems fine to be called after "app" is created.)

    https://flask.palletsprojects.com/en/1.1.x/logging/#basic-configuration

    """

    logger_name = __name__.split(".")[0]
    # i.e., "acondbs" (__name__ = "acondbs._logging")

    logger_level = "DEBUG"  # 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "{asctime} {levelname:>8s} {pathname}:{lineno}: {message}",
                    "style": "{",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                }
            },
            "loggers": {
                logger_name: {"level": logger_level, "handlers": ["wsgi"]}
            },
        }
    )


##__________________________________________________________________||
