import re
import functools
import logging
import pathlib
import os
import sys
from collections import Mapping


def get_data_record(record: logging.LogRecord) -> tuple:
    order_action = getattr(record, 'order_action', {})
    order_id = order_action.get('order_id')
    action_id = order_action.get('action_id')
    graph_id = order_action.get('graph_id')
    node = getattr(record, 'node', None)
    action_type = getattr(record, 'action_type', None)
    orchestrator_id = getattr(record, 'orchestrator_id', None)
    return order_id, action_id, graph_id, node, action_type, orchestrator_id


def get_graph_logger(*, logger=None, logger_name=None, graph=None,
                     order_action=None, node=None, action_type=None, orchestrator_id=None):
    assert bool(logger) != bool(logger_name)  # please specify logger of logger_name
    if logger_name:
        logger = logging.getLogger(logger_name)

    if graph:
        extra = {
            "order_action": graph.order_action.__dict__,
            "node": graph.path,
            "orchestrator_id": graph.id
        }
    else:
        extra = {
            "order_action": order_action.__dict__,
            "node": node,
            "orchestrator_id": orchestrator_id
        }
    extra["action_type"] = action_type

    return logging.LoggerAdapter(logger, extra=extra)


def get_request_client_ip(headers):
    check_headers = {'HTTP_CLIENT_IP', 'HTTP_X_FORWARDED_FOR', 'HTTP_X_FORWARDED',
                     'HTTP_X_CLUSTER_CLIENT_IP', 'HTTP_FORWARDED_FOR', 'HTTP_FORWARDED', 'REMOTE_ADDR'}

    if isinstance(headers, Mapping):
        for header in check_headers:
            value = headers.get(header)
            if header == 'HTTP_X_FORWARDED_FOR' and value:
                value = value.split(',', 1)[0].strip()
                return value

            if value:
                return value
        return None

    for name, value in headers:
        if name.decode("ascii") in check_headers and value:
            if isinstance(name, bytes):
                name = name.decode("ascii")
            if isinstance(value, bytes):
                value = value.decode("ascii")

            if name == "HTTP_X_FORWARDED_FOR":
                value = value.split(',', 1)[0].strip()
            return value
    return None


def singleton(fn):
    """
        Execute function only single time
    """
    stub = object()

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        initialized = getattr(fn, "_initialized", stub)
        if initialized is stub:
            res = fn(*args, **kwargs)
            fn._initialized = res
            return res
        else:
            return initialized
    return wrapper


@singleton
def root_dir(stack_level=2):
    import inspect

    filename = None

    # find the first frame not from standard library
    for frame in inspect.stack(0)[stack_level:]:
        fname = frame.filename.lower()
        if ("site-packages" not in fname and "jetbrains" not in fname and
                not re.search(r"python\d*[\\/]lib", fname) and  # default library folder in linux
                not re.search(r"\\lib\\python", fname)):  # in macos
            filename = frame.filename
            break

    # try to find .git folder
    if filename:
        parents = pathlib.Path(filename).parents
        for parent in parents:
            for path in parent.iterdir():
                if (path.is_dir() and path.name in (".git", ".idea", "venv")) or \
                   path.name in ("requirements.txt", ):
                    return parent

    bin_path = pathlib.Path(sys.argv[0]).parent
    return bin_path


def strtobool(value, default=None):
    if not value:
        return default

    value = value.lower()
    if value in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif value in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"invalid truth value {value}")


def env_get_bool(name, default):
    value = os.environ.get(name)
    return strtobool(value, default)
