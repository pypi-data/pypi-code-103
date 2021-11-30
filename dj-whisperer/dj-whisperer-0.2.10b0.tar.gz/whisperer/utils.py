import logging
from datetime import datetime

from celery import current_app
from django.core.cache import cache
from django.utils.encoding import force_str

logger = logging.getLogger(__name__)


class LockTask(current_app.Task):
    """this abstract class ensures the same tasks run only once at a time"""

    abstract = True

    def __init__(self, *args, **kwargs):
        super(LockTask, self).__init__(*args, **kwargs)

    @staticmethod
    def is_exists_cache_key(lock_cache_key):
        return True if cache.get(lock_cache_key) else False

    def generate_lock_cache_key(self, *args, **kwargs):
        args_key = [force_str(arg) for arg in args]
        kwargs_key = [
            '{}_{}'.format(k, force_str(v)) for k, v in sorted(kwargs.items())
        ]
        return '_'.join([self.name] + args_key + kwargs_key)

    def __call__(self, *args, **kwargs):
        """check task"""
        lock_cache_key = self.generate_lock_cache_key(*args, **kwargs)
        lock_time = datetime.now().isoformat()
        if not self.is_exists_cache_key(lock_cache_key):
            cache.set(lock_cache_key, lock_time, timeout=2 ** self.request.retries)
            return self.run(*args, **kwargs)
        else:
            logger.info("Task %s is already running.." % self.name)


class Registry(object):
    def __init__(self):
        self._registry = {}

    def __contains__(self, key):
        return key in self._registry

    def __getitem__(self, key):
        return self._registry[key]

    def register(self, key):
        def decorator(cls):
            self._registry[key] = cls
            return cls

        return decorator
