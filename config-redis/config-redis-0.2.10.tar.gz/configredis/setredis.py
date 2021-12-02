from time import time
from json import loads, dumps
from redis import ConnectionPool, StrictRedis
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SetRedis:
    def __init__(self, host=None, port=6379, db=0, decode_responses=True, **kwargs):
        """
        :param kwargs: redis config args.
        """
        self.__conf_redis = {**{'host': host, 'port': port, 'db': db},
                             **kwargs} if host else {}
        self.redis = StrictRedis(connection_pool=ConnectionPool(**{**self.connetion(), **self.__conf_redis}),
                                 decode_responses=decode_responses)

    def connetion(self):
        """
        get redis config form your environ or enter.
        redis config name use >CONF_FOR_REDISCONF<
        :return: dict of redis config
        """
        try:
            redis_conf = self.__conf_redis or eval(os.environ['CONF_FOR_REDISCONF'])
        except KeyError:
            os.environ['CONF_FOR_REDISCONF'] = input(
                "WARNING:\n Haven't catch redis config from your env.\n Entry CONF_FOR_REDISCONF args：")
            redis_conf = eval(os.environ['CONF_FOR_REDISCONF'])
        return redis_conf

    def getkeys(self):
        """
        get all fields from redis.
        :return: get fields(keys) list
        """
        return self.redis.keys()

    def getconf(self, name):
        """
        get value according fields.
        :param name: redis fields
        :return: get keys and values according fields.
        """
        res = self.redis.zrevrange(name, 0, 0)
        if res:
            return loads(self.redis.zrevrange(name, 0, 0)[0])
        else:
            return {}

    def set_conf(self, name, mapping=None, notify=True, **kwargs):
        """
        create or update mapping according fields.
        :param notify: show log notice.
        :param name: redis key
        :param mapping: <dict> data what is create or update
        """
        mapping = {**mapping, **kwargs} if mapping else kwargs
        if mapping:
            mapping = {dumps(mapping): int(time())}
            self.redis.zadd(name, mapping)
            logger.info(f"→{name}← has been setup the mapping: →{mapping}← done.") if notify else None
