from databricksbundle.spark.config.ConfiguratorInterface import ConfiguratorInterface


class DictConfigConfigurator(ConfiguratorInterface):
    def __init__(
        self,
        dict_config: dict = None,
    ):
        self.__dict_config = dict_config or dict()

    def get_config(self):
        return self.__dict_config
