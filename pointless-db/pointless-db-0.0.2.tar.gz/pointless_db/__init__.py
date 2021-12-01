from sqlDash import BasePlugin, PluginField, PluginDisplayError
from typing import Dict, List


__version__ = "0.0.2"
__author__ = "WardPearce"
__url__ = "https://github.com/sqlDash/pointless-db-plugin"
__description__ = "Pointless in-memory database for sqlDash"


class PointlessDbPlugin(BasePlugin):
    fields = {
        "name": PluginField(required=True)
    }

    plugin_id = "pointless_db"

    icon = "https://i.imgur.com/U7ceZh4.png"

    pypi_package = "pointless_db"

    version = __version__

    author = __author__

    repo = __url__

    description = __description__

    built_for = "0.0.1"

    # Our pointless memory based "database"
    # Example
    # "name": {
    #     "database_1": {
    #         "table_1": {},
    #         "table_2": {}
    #     },
    #     "database_2": {
    #         "table_1": {},
    #         "table_2": {}
    #     }
    # }

    __databases: Dict[str, Dict[str, Dict[str, dict]]] = {}

    def create_database(self, name: str) -> None:
        if name in self.__databases:
            raise PluginDisplayError("Database already exists.")

        self.__databases[name] = {}

    @property
    def databases(self) -> Dict[str, List[str]]:
        databases = {}
        for database, table in self.__databases.items():
            databases[self.details["name"]][database] = list(table.keys())

        return databases


def loader():
    """Return list of plugins to load.
    """

    return [PointlessDbPlugin]
