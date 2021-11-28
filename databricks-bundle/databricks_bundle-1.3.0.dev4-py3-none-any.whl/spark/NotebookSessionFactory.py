from typing import List
from pyspark.sql.session import SparkSession
from pyspark.context import SparkContext
from pyspark.conf import SparkConf
from databricksbundle.spark.SparkSessionLazy import SparkSessionLazy
from databricksbundle.spark.config.ConfiguratorInterface import ConfiguratorInterface


class NotebookSessionFactory:
    def __init__(
        self,
        configurators: List[ConfiguratorInterface],
    ):
        self.__configurators = configurators

    def create(self) -> SparkSessionLazy:
        import IPython

        all_config = dict()

        for configurator in self.__configurators:
            all_config = {**all_config, **configurator.get_config()}

        spark_conf = SparkConf()
        for key, val in all_config.items():
            spark_conf.set(key, val)

        spark_context = SparkContext.getOrCreate(spark_conf)

        spark = SparkSession(spark_context)

        for key, val in all_config.items():
            spark._jsparkSession.sessionState().conf().setConfString(key, val)

        IPython.get_ipython().user_ns["spark"] = spark

        return SparkSessionLazy(lambda: spark)
