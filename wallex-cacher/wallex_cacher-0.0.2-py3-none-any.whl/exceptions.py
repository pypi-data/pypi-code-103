class CacheException(BaseException):
    pass


class EmptyCacheException(CacheException):
    pass


class RedisError(CacheException):
    pass
