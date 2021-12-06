from .clients import hw_redis_client


class HuaweiRedis:

    def __init__(self, object):
        self.object = object

    @classmethod
    def create(self, params):
        response = hw_redis_client.create_redis(params).instances[0].instance_id
        return response

    @classmethod
    def get_redis(cls, params=None):
        response = hw_redis_client.get_redis_info(params)
        return response

    @classmethod
    def delete(cls, params):
        response = hw_redis_client.delete_redis(params)
        return response

    @classmethod
    def add_white(cls, params):
        response = hw_redis_client.add_white_IP(params)
        return response

    @classmethod
    def get_white_list(cls, params):
        response = hw_redis_client.get_white(params).whitelist
        return response
