# 工具箱中的工具都是开箱即用的，不依赖特别的数据、配置和业务逻辑

from sometools.async_tools.redis_tools.async_io_redis import GeneralAsyncIoRedis


class CommonAsyncTools(GeneralAsyncIoRedis):
    def __init__(self, *args, **kwargs):
        super(CommonAsyncTools, self).__init__(*args, **kwargs)
