from abc import ABC, abstractmethod
from pyspark.sql.session import SparkSession


class ConfiguratorInterface(ABC):

    # @deprecated, please use get_config() instead
    def configure(self, spark: SparkSession):
        for key, val in self.get_config().items():
            spark.conf.set(key, val)

    @abstractmethod
    def get_config(self) -> dict:
        pass
