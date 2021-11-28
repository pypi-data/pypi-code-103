from box import Box
from pyspark.dbutils import DBUtils
from databricksbundle.dbutils.IPythonDbUtilsResolver import resolve_dbutils
from databricksbundle.storage.StorageConfiguratorInterface import StorageConfiguratorInterface


class AzureGen2Configurator(StorageConfiguratorInterface):
    def __init__(self, dbutils: DBUtils):
        self.__dbutils = dbutils

    def get_config(self, storage_config: Box):
        dbutils = resolve_dbutils()
        # TODO: dbutils nějak vytahnout z containeru nebo z ipython user_ns?
        spark_client_secret = dbutils.secrets.get(scope="unit-kv", key="dbx-client-secret")
        client_id = dbutils.secrets.get(scope=storage_config.client_id.secret_scope, key=storage_config.client_id.secret_key)
        client_secret = dbutils.secrets.get(scope=storage_config.client_secret.secret_scope, key=storage_config.client_secret.secret_key)

        return {
            "spark.client_secret": spark_client_secret,  # TODO: tohle je k čemu?
            f"fs.azure.account.auth.type.{storage_config.storage_name}.dfs.core.windows.net": "OAuth",
            f"fs.azure.account.oauth.provider.type.{storage_config.storage_name}.dfs.core.windows.net": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
            f"fs.azure.account.oauth2.client.endpoint.{storage_config.storage_name}.dfs.core.windows.net": f"https://login.microsoftonline.com/{storage_config.tenant_id}/oauth2/token",
            f"fs.azure.account.oauth2.client.id.{storage_config.storage_name}.dfs.core.windows.net": client_id,
            f"fs.azure.account.oauth2.client.secret.{storage_config.storage_name}.dfs.core.windows.net": client_secret,
        }

    def get_type(self):
        return "azure_gen2"
