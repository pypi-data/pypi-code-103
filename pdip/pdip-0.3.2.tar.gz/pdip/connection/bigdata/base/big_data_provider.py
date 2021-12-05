from injector import inject

from .big_data_context import BigDataContext
from .big_data_policy import BigDataPolicy
from ...models.enums import ConnectorTypes
from ....configuration.models.database import DatabaseConfig
from ....dependency import IScoped


class BigDataProvider(IScoped):
    @inject
    def __init__(self):
        pass

    def __initialize_context(self, config: DatabaseConfig):
        database_policy = BigDataPolicy(database_config=config)
        database_context: BigDataContext = BigDataContext(database_policy=database_policy)
        return database_context

    def get_context_by_config(self, config: DatabaseConfig) -> BigDataContext:
        return self.__initialize_context(config=config)

    def get_context(self, connector_type: ConnectorTypes, host, port, user, password,
                    database=None) -> BigDataContext:
        """
        Creating Context
        """
        if connector_type == connector_type.Impala:
            config = DatabaseConfig(type=connector_type.Impala.name,
                                    host=host, port=port,
                                    user=user, password=password,
                                    database=database)
        else:
            raise Exception(f"{connector_type.name} connector type not supported")

        return self.__initialize_context(config=config)
