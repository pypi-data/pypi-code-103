import importlib

from injector import inject

from .big_data_connector import BigDataConnector
from ...models.enums import ConnectorTypes
from ....configuration.models.database import DatabaseConfig


class BigDataPolicy:
    @inject
    def __init__(self, database_config: DatabaseConfig):
        self.database_config = database_config
        self.connector: BigDataConnector = None
        self.connector_name = None
        database_connector_base_module = "pdip.connection.bigdata.connectors"
        if database_config.type == ConnectorTypes.Impala.name:
            connector_namespace = "impala"
            connector_name = "ImpalaConnector"
        else:
            raise Exception("Connector type not found")
        module = importlib.import_module(".".join([database_connector_base_module, connector_namespace]))
        connector_class = getattr(module, connector_name)
        if connector_class is not None:
            self.connector: BigDataConnector = connector_class(database_config)
