import json
import datetime
import logging
import orjson
from .utils import get_data_record

COLOR_MAPPING = {
    'INFO': '\33[32m',
    'WARNING': '\33[33m',
    'CRITICAL': '\33[35m',
    'ERROR': '\33[31m'
}


class OrderJsonFormatter(logging.Formatter):

    def format(self, record):
        order_id, action_id, graph_id, node, action_type, orchestrator_id = get_data_record(record)
        return json.dumps(
            {
                '@timestamp': datetime.datetime.utcnow().isoformat()[:-3] + 'Z',
                'level': record.levelname,
                'text': super().format(record),
                'order_id': order_id,
                'action_id': action_id,
                'graph_id': graph_id,
                'node': node,
                'action_type': action_type,
                'orchestrator_id': orchestrator_id
            }
        )


class JsonFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, multi_line=None):
        self.multi_line = multi_line
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate)
        self._skip_extra = {"name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module",
                            "exc_info", "exc_text", "stack_info",
                            "lineno", "funcName", "created", "msecs", "relativeCreated",
                            "thread", "threadName", "processName", "process", "request_id", "progname"}

    @staticmethod
    def _default_to_str(value):
        return str(value)
    
    def get_extra(self, record):
        extra = {name: value for name, value in record.__dict__.items() if name not in self._skip_extra}
        return extra

    def format(self, record):
        payload = {
            "message": record.getMessage()
        }

        message = {
            "timestamp": datetime.datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "progname": record.__dict__.get("progname", ""),
            "request_id": record.__dict__.get("request_id", ""),
            "tags": record.__dict__.get("tags", None),
            "payload": payload,
        }

        aux = {
            'module': record.module,
            "lineno": record.lineno,
            "func_name": record.funcName,
            "process": record.process,
            "thread_name": record.threadName,
            "logger_name": record.name
        }
        payload["aux"] = aux

        if record.exc_info is not None:
            payload["backtrace"] = self.formatException(record.exc_info)

        payload['args'] = record.args
        payload["extra"] = self.get_extra(record)
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


class OrderConsoleFormatter(logging.Formatter):

    def format(self, record):
        order_id, action_id, graph_id, node, action_type, orchestrator_id = get_data_record(record)
        timestamp = datetime.datetime.utcnow().isoformat()[:-3] + 'Z'
        color = COLOR_MAPPING.get(record.levelname) or '\33[34m'
        request_id = record.__dict__.get("request_id", "")
        if request_id:
            request_id = f"[{request_id}]"
        return f'{color}{request_id} msg: {super().format(record)}\n' \
               f'timestamp: {timestamp}\n' \
               f'level: {record.levelname}\n' \
               f'order_id: {order_id}\n' \
               f'action_id: {action_id}\n' \
               f'graph_id: {graph_id}\n' \
               f'node: {node}\n' \
               f'action_type: {action_type}\n' \
               f'orchestrator_id: {orchestrator_id}\n' \
               f'{record.pathname}:{record.lineno}\n'


class DefaultColoredFormatter(logging.Formatter):

    def format(self, record):
        t = self.formatTime(record)
        level = record.levelname
        line = record.lineno
        color = COLOR_MAPPING.get(level) or '\33[34m'  # blue
        default_color = '\33[0m'
        msg = record.getMessage()
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        s = f'{color}{t} {level} {record.__dict__.get("request_id", "")}\n' \
            f'{record.pathname} line {line}{default_color}\n' \
            f'{msg}\n'

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)

        return s
