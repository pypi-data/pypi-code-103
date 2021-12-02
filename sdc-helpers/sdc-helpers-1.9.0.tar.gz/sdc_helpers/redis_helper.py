"""
   SDC Redis helper module
"""
import os
import redis

class RedisHelper:
    """
       Redis helper class
    """
    redis_conn = None
    def __init__(self, host: str = None, port: str = None, db: int = None):
        # temporary fix - these should be passed at init time
        if host is None:
            host = os.getenv('REDIS_HOST', 'localhost')
        # temporary fix - these should be passed at init time
        if port is None:
            port = int(os.getenv('REDIS_PORT', '6379'))
        # temporary fix - these should be passed at init time
        if db is None:
            db = int(os.getenv('REDIS_DB', '0'))
        try:
            self.redis_conn = redis.Redis(
                host=host,
                port=port,
                db=db
            )
        except redis.ConnectionError as exception:
            print(exception)

    def __del__(self):
        self.redis_conn.connection_pool.disconnect()

    def redis_set(self, *, key: str, value: str, expiry: int = None):
        """
            Set a Redis key with the specified value

            args:
                key (str): The Redis key
                value (str): The value to set
                expiry (int): A TTL for the specified key
        """
        self.redis_conn.set(key, value, expiry)

    def redis_get(self, *, key: str) -> str:
        """
            Get a Redis key

            args:
                key (str): The Redis key

            return:
                value (str) : Returns the value for the specified key

        """
        return self.redis_conn.get(key)

    def redis_keys(self, *, pattern: str) -> list:
        """
            Get a list of Redis keys matching a pattern

            args:
                pattern (str): The pattern to search for

            return:
                keys (list) : Returns a list of keys found

        """
        keys = []
        for key in self.redis_conn.keys(pattern):
            keys.append(key.decode("utf-8"))

        return keys

    def redis_delete(self, *, keys) -> int:
        """
            Delete a Redis key

            args:
                key (str/list): One or many Redis keys

            return:
                result (int) : The number of keys deleted

        """
        if isinstance(keys, str):
            keys = [keys]
        return self.redis_conn.delete(*keys)

    def redis_flushall(self, asynchronous: bool = False):
        """Delete all keys in all databases on current host

        Args:
            asynchronous (bool): whether server can run flush asynchronously
        """
        self.redis_conn.flushall(asynchronous=asynchronous)

    def redis_flush_keys_matching(self, pattern: str = None):
        """
            Delete all keys matching pattern in database.
            Lookups up keys using SCAN and then mass deletes using
            redis_delete.

        Args:
            pattern (str, optional): A redis format pattern for matching keys. Defaults to None.

        Raises:
            Exception: [description]
        """
        if pattern is None:
            raise Exception((
                "No pattern given. To delete all keys, "
                "pattern = '*' or use a more specific pattern to match keys with "
            ))

        keys = list(self.redis_conn.scan_iter(pattern))
        self.redis_conn.delete(*keys)

    def redis_hexists(self, *, hashkey: str):
        """Check hashkey exists in store"""
        return self.redis_conn.exists(hashkey)

    def redis_h_check_key_exists(self, *, hashkey: str, key: str):
        """Check key exists in haskey in store"""
        return self.redis_conn.hexists(hashkey, key)

    def redis_hset(
            self,
            *,
            hashkey: str,
            key: str = None,
            value: str = None,
            dict_obj: dict = None
    ):
        """
            Create or Overwrite dictionary hash store.
            Either takes a dict_obj or (key, value) pair.
        """
        if dict_obj is not None:
            self.redis_conn.hset(name=hashkey, mapping=dict_obj)
        elif key is not None and value is not None:
            self.redis_conn.hset(name=hashkey, key=key, value=value)
        else:
            raise ValueError("Expected either dict_obj or key & value")

    def redis_hmget(self, *, hashkey: str, keys: list):
        """Read values for set of keys from hash store"""
        return self.redis_conn.hmget(name=hashkey, keys=keys)

    def redis_hget(self, *, hashkey: str, key: str):
        """Read values for a given key from hash store"""
        return self.redis_conn.hget(name=hashkey, key=key)

    def redis_hmgetall(self, *, hashkey: str):
        """Read complete dict object from hash store"""
        return self.redis_conn.hgetall(name=hashkey)
