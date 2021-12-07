__all__ = (
    "get_log_config",
    "JSON_FIELDS"
)

JSON_FIELDS = (
    "asctime", "message", "name", "created",
    "filename", "module", "funcName", "lineno",
    "msecs", "pathname", "process", "processName",
    "relativeCreated", "thread", "threadName", "levelname",
    "access",
)


def build_log_format(fields):
    return " ".join(f"%({f})s" for f in fields)


def get_log_config(
    filter_gunicorn_access=True,
    filter_uvicorn_access=True,
    json_formatter_cls=None,
    fields=JSON_FIELDS,
):
    """
    Get log config for Gunicorn+Uvicorn
    """
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                "format": build_log_format(fields=fields),
                "class": json_formatter_cls or "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'formatter': 'json',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
            'stderr': {
                'level': 'NOTSET',
                'formatter': 'json',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stderr',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'WARNING',
            },
            'gunicorn.error': {
                'handlers': ['stderr'],
                'level': 'INFO',
                'propagate': False,
            },
            'gunicorn': {
                'handlers': [],
                'level': 'NOTSET',
                'propagate': True,
            },
            'gunicorn.access': {
                'handlers': [] if filter_gunicorn_access else ["stderr"],
                'level': 'INFO',
                'propagate': False,
            },
            'gunicorn.http.asgi': {
                'handlers': [],
                'level': 'NOTSET',
                'propagate': True,
            },
            'gunicorn.http': {
                'handlers': [],
                'level': 'NOTSET',
                'propagate': True,
            },
            "uvicorn": {
                'handlers': [],
                'level': 'NOTSET',
                'propagate': True,
            },
            "uvicorn.error": {
                'handlers': ['stderr'],
                'level': 'INFO',
                'propagate': True,
            },
            "uvicorn.access": {
                "handlers": [] if filter_uvicorn_access else ["stderr"],
                "level": 'INFO',
                "propagate": True
            },
        }
    }
