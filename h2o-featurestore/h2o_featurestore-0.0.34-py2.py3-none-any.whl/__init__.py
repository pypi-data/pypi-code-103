import zipfile
from codecs import open
from os import path

from featurestore.client import Client
from featurestore.core.client_config import ClientConfig
from featurestore.core.data_source_wrappers import (
    CSVFile,
    CSVFolder,
    DeltaTable,
    DeltaTableFilter,
    DriverlessAIMOJO,
    JdbcTable,
    JoinedFeatureSets,
    JSONFile,
    JSONFolder,
    ParquetFile,
    ParquetFolder,
    PartitionOptions,
    Proxy,
    SnowflakeCursor,
    SnowflakeTable,
    SparkDataFrame,
    SparkPipeline,
)
from featurestore.core.schema import Column, Schema


def __get_version():
    here = path.abspath(path.dirname(__file__))
    if ".zip" in here:
        with zipfile.ZipFile(here[: -len("featurestore/")], "r") as archive:
            return archive.read("featurestore/version.txt").decode("utf-8").strip()
    else:
        with open(path.join(here, "version.txt"), encoding="utf-8") as f:
            return f.read().strip()


__version__ = __get_version()
__all__ = [
    "Client",
    "Column",
    "CSVFile",
    "JSONFile",
    "ParquetFile",
    "SnowflakeTable",
    "JdbcTable",
    "PartitionOptions",
    "DriverlessAIMOJO",
    "SnowflakeCursor",
    "DeltaTable",
    "JoinedFeatureSets",
    "SparkPipeline",
    "Proxy",
    "JSONFolder",
    "Schema",
    "SparkDataFrame",
    "ClientConfig",
]
