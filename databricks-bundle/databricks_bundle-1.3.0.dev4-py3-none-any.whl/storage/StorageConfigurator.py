from box import Box
from typing import List, Dict
from databricksbundle.storage.StorageConfiguratorInterface import StorageConfiguratorInterface
from databricksbundle.spark.config.ConfiguratorInterface import ConfiguratorInterface


class StorageConfigurator(ConfiguratorInterface):

    __storage_configurators: Dict[str, StorageConfiguratorInterface]

    def __init__(self, storages: Box, storage_configurators: List[StorageConfiguratorInterface]):
        self.__storages = storages
        self.__storage_configurators = {
            storage_configurator.get_type(): storage_configurator for storage_configurator in storage_configurators
        }

    def get_config(self) -> dict:
        all_config = dict()

        for key, storage_config in self.__storages.items():
            if storage_config.type not in self.__storage_configurators:
                raise Exception(f"No configurator for storage: {storage_config.type}")

            storage_configurator = self.__storage_configurators[storage_config.type]

            all_config = {**all_config, **storage_configurator.get_config(storage_config)}

        return all_config
