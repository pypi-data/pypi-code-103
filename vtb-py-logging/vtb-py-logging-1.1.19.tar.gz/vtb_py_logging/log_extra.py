import contextvars
import contextlib
import copy
import types
import logging


_log_context = contextvars.ContextVar("log_context", default={})


@contextlib.contextmanager
def log_extra(**kwargs):
    current_context = _log_context.get()
    new_context = copy.deepcopy(current_context)
    new_context.update(kwargs)
    reset_token = _log_context.set(new_context)
    yield new_context
    _log_context.reset(reset_token)


def push_extra(**kwargs):
    current_context = _log_context.get()
    new_context = copy.deepcopy(current_context)
    new_context.update(kwargs)
    return _log_context.set(new_context)


def pop_extra(reset_token):
    _log_context.reset(reset_token)


class ExtraLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=2):
        context_extra = _log_context.get()
        extra = extra or {}
        extra.update(context_extra)
        super()._log(level, msg, args, exc_info=exc_info, extra=extra,
                     stack_info=stack_info, stacklevel=stacklevel)


def _patch_log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
    context_extra = _log_context.get()
    extra = extra or {}
    extra.update(context_extra)
    self._orig_log(level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel)


class KeyErrorLessDict(dict):
    def __getitem__(self, key):
        return dict.get(self, key, "")


def _patch_format(self, record):
    return self._fmt % KeyErrorLessDict(record.__dict__)


_initialized = False


def _patch_logger(logger):
    if not hasattr(logger, "_orig_log"):
        logger._orig_log = logger._log
        logger._log = types.MethodType(_patch_log, logger)


# noinspection PyProtectedMember
def init_extra_logger():
    global _initialized
    if _initialized:
        return
    _initialized = True

    logging.setLoggerClass(ExtraLogger)
    for name, logger in logging.Logger.manager.loggerDict.items():
        if not isinstance(logger, ExtraLogger) and not isinstance(logger, logging.PlaceHolder):
            _patch_logger(logger)
    _patch_logger(logging.root)
    logging.PercentStyle._format = _patch_format


def get_extra():
    return _log_context.get() or {}
