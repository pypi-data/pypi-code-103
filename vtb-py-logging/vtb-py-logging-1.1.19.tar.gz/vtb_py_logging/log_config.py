import logging
import os
import functools
import pathlib
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from vtb_py_logging import JsonFormatter, DefaultColoredFormatter
from vtb_py_logging.utils import root_dir, env_get_bool

try:
    import logbook
    has_logbook = True
except ImportError:
    has_logbook = False


class LogConfigure:
    DEFAULT_FORMAT = "%(asctime)s[%(levelname)7s][%(threadName)s][%(request_id)10s] %(message)s"
    # used in interactive shell scripts
    DEFAULT_USER_CONSOLE_FORMAT = "%(timeonly)s[%(levelname)7s] %(message)s"
    DEFAULT_OUTPUTS = "json,stderr"
    DEFAULT_DEV_OUTPUTS = "simple,stderr"

    FORMAT_MAP = {"console": "stderr"}

    def __init__(self, app_name=None, filename=None, format_string=None, level=None, rotate_mb=None,
                 rotate_when=None, backup_count=7, json_multiline=False, request_id_support=True,
                 log_output=None, colored=True, log_dir=None, log_sql=None, log_celery=False,
                 pika_log_level=None, format_string_user_console=None, cleanup=False):
        self.app_name = app_name
        self._format_string = format_string
        self._format_string_user_console = format_string_user_console
        self._level = level
        self.rotate_mb = rotate_mb
        self.rotate_when = rotate_when
        self.backup_count = backup_count
        self.json_multiline = json_multiline
        self.request_id_support = True
        self._log_output = log_output
        self._colored = colored
        self._log_dir = log_dir
        self._filename = pathlib.Path(filename) if filename else None
        self.request_id_support = request_id_support
        self._apply_suffix = False
        self._log_sql = log_sql
        self.log_celery = log_celery
        self._pika_log_level = pika_log_level
        self.cleanup = cleanup

    @property
    def colored(self):
        return os.environ.get("LOG_COLORED", self._colored)

    @functools.cached_property
    def is_dev_machine(self):
        return os.name == "nt" or "PYCHARM_HOSTED" in os.environ

    @functools.cached_property
    def directory(self):
        log_dir = os.environ.get("LOG_DIR")
        if log_dir:
            return pathlib.Path(log_dir)

        if self._filename and self._filename.is_absolute():
            directory = self._filename.parent
            return directory
        if self.is_dev_machine:
            return root_dir() / "log"

        return pathlib.Path("/var/log/", self.app_name)

    def get_filename(self, suffix):
        if self._filename:
            filename = self._filename
        else:
            filename = os.environ.get("LOG_FILENAME", f"{self.app_name}.log")
        filename = self.directory / filename
        if self._apply_suffix:
            filename.with_suffix(suffix)

        self._apply_suffix = True
        return filename

    @property
    def format_string(self):
        return self._format_string or self.DEFAULT_FORMAT

    @property
    def format_string_user_console(self):
        return self._format_string_user_console or self.DEFAULT_USER_CONSOLE_FORMAT

    def _get_file_handler(self, suffix):
        filename = self.get_filename(suffix)
        if self.rotate_mb:
            handler = RotatingFileHandler(filename, maxBytes=self.rotate_mb * 1024 * 1024,
                                          backupCount=self.backup_count, encoding="utf-8")

        elif self.rotate_when:
            handler = TimedRotatingFileHandler(filename, when=self.rotate_when,
                                               backupCount=self.backup_count, encoding="utf-8")
        else:
            handler = logging.FileHandler(filename, encoding="utf-8")
        return handler

    def get_handler(self, name):
        if name == "simple":
            handler = self._get_file_handler(".txt")
            formatter = logging.Formatter(self.format_string)
            handler.setFormatter(formatter)
        elif name == "json":
            handler = self._get_file_handler(".json")
            formatter = JsonFormatter(multi_line=self.json_multiline)
            handler.setFormatter(formatter)
        elif name == "stderr":
            handler = logging.StreamHandler()
            formatter = DefaultColoredFormatter(self.format_string) if self.colored else \
                logging.Formatter(self.format_string)
            handler.setFormatter(formatter)
        else:
            raise ValueError(f"unknown handler type: '{name}'")

        return handler

    @property
    def level(self):
        return os.environ.get("LOG_LEVEL", self._level or "INFO")

    def normalize_format_names(self, names: str):
        names = names.lower().split(",")
        return [self.FORMAT_MAP.get(name, name) for name in names]

    @property
    def formats(self):
        if self._log_output:
            names = self._log_output
        else:
            names = os.environ.get("LOG_OUTPUT") or os.environ.get("LOG_FORMAT")
        if not names:
            names = self.DEFAULT_DEV_OUTPUTS if self.is_dev_machine else self.DEFAULT_OUTPUTS
        return self.normalize_format_names(names)

    def get_handlers(self, names):
        handlers = [self.get_handler(name) for name in names]
        return handlers

    @property
    def log_sql(self):
        if self._log_sql is not None:
            return self._log_sql
        return env_get_bool("LOG_SQL", False)

    @property
    def pika_log_level(self):
        if self._pika_log_level is not None:
            return self._pika_log_level
        return os.environ.get("LOG_PIKA_LEVEL", "WARNING")

    @property
    def default_logger_level(self):
        return os.environ.get("LOGGING_DEFAULT_LEVEL") or os.environ.get("LOG_DEFAULT_LEVEL")

    @property
    def default_logger_output(self):
        return os.environ.get("LOGGING_DEFAULT_HANDLER") or os.environ.get("LOG_DEFAULT_OUTPUT")


if has_logbook:
    class LogConfigureLogbook(LogConfigure):
        DEFAULT_FORMAT = "{record.time:%Y-%m-%d %H:%M:%S.%f}[{record.level_name:>7}]" \
                         "[{record.thread_name:>5}][{record.extra[request_id]:>10}] {record.message}"

        DEFAULT_USER_CONSOLE_FORMAT = "{record.time:%H:%M:%S.%f} [{record.level_name:>7}] {record.message}"

        def _get_file_handler(self, suffix):
            filename = self.get_filename(suffix)
            if self.rotate_mb:
                return logbook.RotatingFileHandler(
                    filename, format_string=self.format_string, level=self.level,
                    delay=True, max_size=self.rotate_mb * 1024 * 1024, backup_count=self.backup_count)

            if self.rotate_when:
                if self.rotate_when == 'H':
                    date_format = "%Y-%m-%d_%H"
                elif self.rotate_when == 'D':
                    date_format = "%Y-%m-%d"
                else:
                    date_format = "%Y-%m-%d"

                return logbook.TimedRotatingFileHandler(
                    filename, format_string=self.format_string, level=self.level,
                    date_format=date_format, backup_count=self.backup_count, encoding="utf-8")

            return logbook.FileHandler(filename, encoding="utf-8", format_string=self.format_string)

        def get_handler(self, name):
            from vtb_py_logging.logbook_configure import JsonFormatter
            from logbook.more import ColorizedStderrHandler
            if name == "console" or name == "stderr":
                if self.colored:
                    handler = ColorizedStderrHandler(format_string=self.format_string)
                else:
                    handler = logbook.StderrHandler(format_string=self.format_string)
            elif name == "management":
                if self.colored:
                    handler = ColorizedStderrHandler(format_string=self.format_string_user_console)
                else:
                    handler = logbook.StderrHandler(format_string=self.format_string_user_console)
                handler.level_name = "INFO"
            elif name == "simple":
                handler = self._get_file_handler(".txt")
            elif name == "json":
                handler = self._get_file_handler(".json")
                formatter = JsonFormatter(multi_line=self.json_multiline)
                handler.formatter = formatter
            else:
                raise ValueError(f"Unknown logger handler type: {name}")
            handler.bubble = True

            return handler
