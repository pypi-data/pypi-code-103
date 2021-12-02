import logging
from vtb_py_logging import log_extra, SQLExtraFilter
from vtb_py_logging.log_config import LogConfigure
from vtb_py_logging.utils import singleton


@singleton
def initialize_logging(app_name: str = None, config: LogConfigure = None):
    if not config:
        config = LogConfigure(app_name=app_name)

    root = logging.root

    if config.cleanup:
        for h in root.handlers[:]:
            root.removeHandler(h)
            h.close()
    root.setLevel(config.level)

    config.directory.mkdir(exist_ok=True)

    handlers = config.get_handlers(config.formats)
    for handler in handlers:
        root.addHandler(handler)

    if config.log_sql:
        try:
            from django.db import connection
            connection.force_debug_cursor = True  # only django specific import
        except ImportError:
            pass
        sql_logger = logging.getLogger("django.db.backends")
        sql_logger.setLevel(logging.DEBUG)
        sql_logger.addFilter(SQLExtraFilter())

    log_extra.init_extra_logger()
    log_extra.push_extra(progname=app_name)

    default_logger = logging.getLogger("default")
    if config.default_logger_level:
        default_logger.setLevel(config.default_logger_level)
        if config.default_logger_output:
            default_logger_handlers = config.normalize_format_names(config.default_logger_output)
            diff = set(default_logger_handlers) - set(config.formats)
            if diff:
                handlers = config.get_handlers(diff)
                for handler in handlers:
                    default_logger.addHandler(handler)
                default_logger.propagate = False
