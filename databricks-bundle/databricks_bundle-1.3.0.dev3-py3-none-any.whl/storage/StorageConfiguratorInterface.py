from abc import ABC
from box import Box


class StorageConfiguratorInterface(ABC):
    def get_config(self, storage_config: Box):
        pass

    def get_type(self) -> str:
        pass
