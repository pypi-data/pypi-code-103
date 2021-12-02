import logging
import logging.config
from .queue0 import RabbitProducer0
from .utils import dump_json, get_current_second, sleep
from .config import config
import traceback
import multiprocessing
from threading import current_thread
import functools
import os

__log_path = '.'


def _get_file_path(root_path, file_name, module_name):
    if len(module_name) == 0:
        return root_path + '/' + file_name
    return root_path + '/' + module_name + '.' + file_name


def _get_config(root_path='.', is_console=True, module_name=''):
    global __is_debug, __log_name
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[{levelname}][{asctime}]{message}',
                'style': '{',
            },
        },
        'handlers': {
            'info': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': _get_file_path(root_path, 'info.log', module_name),
                'encoding': 'utf8',
                'formatter': 'verbose'
            },
            'warn': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                'filename': _get_file_path(root_path, 'warn.log', module_name),
                'encoding': 'utf8',
                'formatter': 'verbose'
            },
            'error': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': _get_file_path(root_path, 'error.log', module_name),
                'encoding': 'utf8',
                'formatter': 'verbose'
            },
        },
    }
    is_django = ('DJANGO_SETTINGS_MODULE' in os.environ)
    if is_django:
        config['filters'] = {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            }
        }
    if __log_name != 'root':
        config['loggers'] = {
            __log_name: {
                'handlers': ['error', 'info', 'warn'],
                'level': 'INFO',
            },
        }
    else:
        config['root'] = {
            'handlers': ['error', 'info', 'warn'],
            'level': 'INFO',
        }
    if is_console:
        config['handlers'] = {
            'console': {
                'class': 'logging.StreamHandler',
            }
        }
        if __log_name != 'root':
            config['loggers'][__log_name] = {
                'handlers': ['console'],
                'level': 'INFO',
            }
        else:
            config['root'] = {
                'handlers': ['console'],
                'level': 'INFO',
            }

    elif __is_debug:
        config['handlers']['debug'] = {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_true'] if is_django else [],
            'filename': _get_file_path(root_path, 'debug.log', module_name),
            'encoding': 'utf8',
            'formatter': 'verbose'
        }
        if is_django:
            if 'loggers' not in config:
                config['loggers'] = dict()
            config['loggers']['django.db.backends'] = {
                'level': 'DEBUG',
                'handlers': ['debug'],
            }
        if __log_name != 'root':
            config['loggers'][__log_name] = {
                'handlers': ['error', 'info', 'warn', 'debug'],
                'level': 'DEBUG',
            }
        else:
            config['root'] = {
                'handlers': ['error', 'info', 'warn', 'debug'],
                'level': 'DEBUG',
            }
    return config


__logger = None
__module = ''
__producer = None
__monit_queue = None
__use_module_name = None

__is_debug = False

__log_process_name = False
__log_thread_name = False
__report_error_log = False

__log_name = 'root'


def set_log_name(log_name):
    global __log_name
    __log_name = log_name


def set_report_error_log(flag):
    global __report_error_log
    __report_error_log = flag


def set_log_process_name(flag):
    global __log_process_name
    __log_process_name = flag


def set_log_thread_name(flag):
    global __log_thread_name
    __log_thread_name = flag


def log_init_config(module='unknown', root_path='.', monit_queue='', use_module_name='', sub_module='', is_dict=False):
    global __logger, __module, __monit_queue, __is_debug, __log_name, __project, __is_dict, __sub_module, __use_module_name
    try:
        __is_debug = (config('settings', 'debug', '0') == '1')
    except Exception as ex:
        print(ex)
    logging.config.dictConfig(_get_config(root_path, root_path == 'console', use_module_name))
    __logger = logging.getLogger(__log_name)
    __monit_queue = monit_queue
    if module is not None:
        __module = module
    __project = module
    __sub_module = sub_module
    __is_dict = is_dict
    __use_module_name = use_module_name
    try:
        __is_debug = (config('settings', 'debug', '0') == '1')
        if not __is_debug:
            logging.getLogger("pika").setLevel(logging.WARNING)
    except Exception as ex:
        print(ex)


def _check_log_init():
    global __logger
    if __logger is None:
        log_init_config()


def _check_producer():
    global __producer, __monit_queue
    if __producer is not None:
        return __producer
    if __monit_queue is None or __monit_queue == '':
        return None
    __producer = RabbitProducer0(__monit_queue)
    return __producer


def _send_monit_message(topic, module, message):
    try:
        global __module, __use_module_name
        if __module is not None and len(module) == 0:
            module = __module
        producer = _check_producer()
        if producer is None:
            return
        if __use_module_name:
            message = "[{0}]{1}".format(__use_module_name, message)
        json = {'module': module, 'message': message, 'time': get_current_second()}
        producer.send(topic, dump_json(json))
    except Exception as ex:
        log_exception(ex, False)


def build_log_msg(msg, **kwargs):
    global __sub_module, __log_name, __project
    _log_msg = {
        'project': __project,
        'module': __sub_module,
        'msg': msg,
    }
    _log_msg.update(kwargs)
    return dump_json(_log_msg)


def log_info(msg, **kwargs):
    global __logger, __is_dict
    if __logger is None:
        return
    if __is_dict:
        __logger.info(build_log_msg(msg, **kwargs))
        return
    __logger.info(_build_log_prefix() + msg)


def log_notice(msg, module=''):
    global __logger, __monit_queue, __module
    if __logger is None:
        return
    if __module is not None and len(module) == 0:
        module = __module
    if len(module) == 0:
        module = 'unknown'
    __logger.info("{0}{1}".format(_build_log_prefix(), msg))
    _send_monit_message('notice_logs', module, msg)


def log_task_schedule(task_name, period, module='', exclude_time=None):
    global __logger, __monit_queue, __module
    if __logger is None:
        return
    if __module is not None and len(module) == 0:
        module = __module
    if len(module) == 0:
        module = 'unknown'
    if not exclude_time:
        exclude_time = ''
    msg = {
        'module': module,
        'task': task_name,
        'period': period,
        'exclude_time': exclude_time
    }
    msg = dump_json(msg)
    __logger.info(_build_log_prefix() + msg)
    _send_task_schedule_message('task_schedule_logs', msg)


def _send_task_schedule_message(topic, msg):
    times = 3
    while times >= 0:
        times -= 1
        producer = None
        try:
            producer = _check_producer()
            if producer is None:
                return
            producer.send(topic, msg)
            return
        except Exception as ex:
            log_exception(ex)
            if producer:
                try:
                    producer.close_connection()
                except:
                    pass
            sleep(2)


def _build_log_prefix():
    global __log_thread_name, __log_process_name
    thread_name = "[" + current_thread().name + "]" if __log_thread_name else ""
    process_name = "[" + multiprocessing.current_process().name + "]" if __log_process_name else ""
    return "{0}{1}".format(process_name, thread_name)


def log_debug(msg):
    global __is_debug
    if __is_debug:
        log_info(msg)


def log_warn(msg, **kwargs):
    global __logger, __is_dict
    if __logger is None:
        return
    if __is_dict:
        __logger.warn(build_log_msg(msg, **kwargs))
        return
    __logger.warn(_build_log_prefix() + msg)


def log_error(msg, **kwargs):
    global __logger, __is_dict, __report_error_log
    if __logger is None:
        return
    if __report_error_log:
        _send_error_message(msg)
    if __is_dict:
        __logger.error(build_log_msg(msg, **kwargs))
        return
    __logger.error(_build_log_prefix() + msg)


def log_fatal(msg):
    global __logger
    if __logger is None:
        return
    __logger.error(str(msg))
    _send_error_message(msg, queue_name="fatal_logs")


def _send_error_message(message, queue_name="error_logs"):
    try:
        global __module, __use_module_name
        module = __module
        if not module:
            module = 'unknown'
        producer = _check_producer()
        if producer is None:
            return
        if __use_module_name:
            message = "[{0}]{1}".format(__use_module_name, message)
        json = {'module': module, 'message': message, 'time': get_current_second()}
        producer.send(queue_name, dump_json(json))
        if is_debug():
            log_info("_send_error_message for queue_name={0} message={1}".format(queue_name, json))
    except Exception as ex:
        log_exception(ex, True)


def raise_exception(msg):
    log_exception(msg)
    raise Exception(msg)


def log_exception(ex, ignore_report=False):
    global __logger, __report_error_log
    if __logger is None:
        return
    msg = '%s%s' % (_build_log_prefix(), ex)
    __logger.exception(msg)
    if __report_error_log and not ignore_report:
        _send_error_message(msg)


def try_catch_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            log_exception(ex)
            return None

    return wrapper


def catch_raise_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            log_exception(ex)
            raise ex

    return wrapper


def while_try_catch_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                log_exception(ex)
                sleep(2)

    return wrapper


def is_debug():
    return config('settings', 'debug', '0') == '1'


def _log_print(msg_dict, log_level):
    log_str = dump_json(msg_dict)
    if log_level == 'INFO':
        log_info(log_str)
    elif log_level == 'WARN':
        log_warn(log_str)
    else:
        log_error(log_str)


def log_format_print(module, project, code, msg, log_level='INFO', **kwargs):
    _log_dict = locals()
    _log_dict.update(_log_dict.pop('kwargs'))
    _log_print(_log_dict, log_level)
