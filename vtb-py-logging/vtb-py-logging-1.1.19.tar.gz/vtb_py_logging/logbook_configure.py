import orjson
import logging
import logbook
import os
import traceback

from vtb_py_logging.log_config import LogConfigureLogbook
from vtb_py_logging.log_extra import get_extra, push_extra
from vtb_py_logging.utils import root_dir, singleton
from logbook.compat import redirect_logging


def inject_extra(record):
    extra = get_extra()
    record.extra.update(extra)


class JsonFormatter:
    def __init__(self, multi_line=False):
        self.multi_line = multi_line

    @staticmethod
    def jsonable(value):
        if value is None or isinstance(value, (int, float, str, bool, dict, list)):
            return value
        return str(value)

    def __call__(self, record, handler):
        line = self.format_record(record, handler)
        return line

    @staticmethod
    def _default_to_str(value):
        return str(value)

    def format_record(self, record, handler):
        payload = {
            "message": record.message
        }

        extra = record.extra.copy()

        message = {
            "timestamp": record.time.isoformat() + "Z",
            "level": logbook.get_level_name(record.level),
            "progname": extra.pop("progname", ""),
            "request_id": extra.pop("request_id", ""),
            "tags": extra.pop("tags", None),
            "payload": payload,
        }

        aux = {
            'module': record.module,
            "lineno": record.lineno,
            "func_name": record.func_name,
            "process": record.process_name,
            "thread_name": record.thread_name,
            "logger_name": record.channel
        }
        payload["aux"] = aux

        if record.exc_info is not None:
            message['stack_trace'] = '\n'.join(traceback.format_exception(*record.exc_info))

        payload['args'] = record.args
        payload["extra"] = extra
        option = orjson.OPT_UTC_Z
        if self.multi_line:
            option |= orjson.OPT_INDENT_2

        try:
            packed = orjson.dumps(message, default=self._default_to_str, option=option)
        except Exception as e:
            m = {str(k): str(v) for k, v in message.items()}
            m["failed_dump"] = str(e)
            packed = orjson.dumps(m, default=self._default_to_str, option=option)
        return packed.decode("utf-8")


def redirect_celery_logs(celery_log_level):
    logger = logging.getLogger("celery")
    logger.setLevel(celery_log_level)
    redirect_logging(logger)

    logger = logging.getLogger("celery.worker")
    logger.setLevel(celery_log_level)
    redirect_logging(logger)

    logger = logging.getLogger('kombu')
    logger.setLevel("INFO")
    redirect_logging(logger)


def get_setup(config: LogConfigureLogbook = None, setup_progname=True):
    config.directory.mkdir(exist_ok=True)
    handlers = config.get_handlers(config.formats)
    handlers.insert(0, logbook.NullHandler())
    handlers.append(logbook.Processor(inject_extra))
    if setup_progname:
        push_extra(progname=config.app_name)
    return logbook.NestedSetup(handlers)


def setup_backend(app_name=None, config: LogConfigureLogbook = None):
    # only config or app_name should be passed
    assert bool(app_name) != bool(config)
    if config is None:
        config = LogConfigureLogbook(app_name)

    setup = get_setup(config)

    if config.log_sql:
        logger = logging.getLogger('sqlalchemy.engine')
        logger.setLevel("DEBUG")
        redirect_logging(logger)
        logger = logging.getLogger('sqlalchemy.engine.base.Engine')
        logger.addHandler(logging.NullHandler())

    logging.getLogger('urllib3').setLevel("INFO")

    if config.log_celery:
        celery_log_level = os.environ.get("LOG_CELERY_LEVEL", "DEBUG")
        redirect_celery_logs(celery_log_level)

    logger = logging.getLogger("pika")
    logger.setLevel(config.pika_log_level)

    return setup


@singleton
def setup_test(stderr=False, **kwargs):
    config = LogConfigureLogbook("test", filename=root_dir() / "log/test.log",
                                 log_output = "simple,stderr" if stderr else "simple",
                                 **kwargs)
    return setup_backend(None, config)


def setup_console(app_name, level=None):
    setup = setup_backend(config=LogConfigureLogbook(app_name, log_output="management,json", level=level))
    return setup

