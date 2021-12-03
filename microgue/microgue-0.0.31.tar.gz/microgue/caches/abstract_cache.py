import datetime
import json
import logging
import redis

logger = logging.getLogger('microgue')


class CacheConnectionFailed(Exception):
    pass


class AbstractCache:
    cache = None
    host = ''
    port = ''
    prefix = ''
    ttl = 900
    connection_timeout = 1
    connection_required = True

    def __init__(self, *args, **kwargs):
        try:
            self.cache = redis.StrictRedis(host=self.host, port=self.port, socket_connect_timeout=self.connection_timeout)
            self.cache.ping()
        except Exception as e:
            logger.error("########## {} Error".format(self.__class__.__name__))
            logger.error("{}: {}".format(e.__class__.__name__, str(e)))
            if self.connection_required:
                raise CacheConnectionFailed(str(e))
            else:
                self.cache = None

    def _prefix_key(self, key):
        if self.prefix:
            return '{}-{}'.format(self.prefix, key)
        else:
            return key

    def get(self, key):
        if self.cache:
            prefixed_key = self._prefix_key(key)
            value = self.cache.get(prefixed_key)
            logger.debug("########## {} Get ##########".format(self.__class__.__name__))
            logger.debug("Key: {}".format(prefixed_key))
            logger.debug("Value: {}".format(value))
            try:
                return json.loads(value)
            except:
                pass
            try:
                return value.decode('ascii')
            except:
                pass
            return value

    def set(self, key, value, ttl=None):
        if self.cache:
            value = value if type(value) is str else json.dumps(value)
            prefixed_key = self._prefix_key(key)
            ttl = ttl if ttl is not None else self.ttl
            logger.debug("########## {} Set ##########".format(self.__class__.__name__))
            logger.debug("Key: {}".format(prefixed_key))
            logger.debug("Value: {}".format(value))
            self.cache.set(prefixed_key, value, ex=ttl)
            return True

    def delete(self, key):
        if self.cache:
            prefixed_key = self._prefix_key(key)
            logger.debug("########## {} Delete ##########".format(self.__class__.__name__))
            logger.debug("Key: {}".format(prefixed_key))
            return bool(self.cache.delete(prefixed_key))

    def expires_at(self, key):
        if self.cache:
            prefixed_key = self._prefix_key(key)
            expire_time = self.cache.ttl(prefixed_key)
            return str(datetime.timedelta(seconds=expire_time))

    def clear(self):
        if self.cache:
            logger.debug("########## Clearing All Cache ##########")
            return bool(self.cache.flushdb())
