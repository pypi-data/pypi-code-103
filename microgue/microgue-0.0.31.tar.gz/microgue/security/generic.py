import logging
from flask import g
from functools import wraps

logger = logging.getLogger('microgue')


def is_allowed_by_all(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        logger.debug('########## Authentication: is_allowed_by_all ##########')
        g.authenticated = True
        return f(*args, **kwargs)
    return wrapped
