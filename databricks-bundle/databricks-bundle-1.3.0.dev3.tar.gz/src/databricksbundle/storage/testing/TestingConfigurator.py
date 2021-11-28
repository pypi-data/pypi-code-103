from box import Box
from databricksbundle.storage.StorageConfiguratorInterface import StorageConfiguratorInterface


class TestingConfigurator(StorageConfiguratorInterface):
    def get_config(self, config: Box):
        return {
            f"testing.storage.{config.storage_name}": f"tenant/{config.tenant_id}",
            f"testing.secrets.{config.storage_name}.client_id": f"secrets/{config.client_id.secret_scope}/{config.client_id.secret_key}",
            f"testing.secrets.{config.storage_name}.client_secret": f"secrets/{config.client_secret.secret_scope}/{config.client_secret.secret_key}",
        }

    def get_type(self):
        return "testing"
