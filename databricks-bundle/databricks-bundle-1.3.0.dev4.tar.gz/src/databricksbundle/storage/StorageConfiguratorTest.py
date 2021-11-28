import unittest
from pyfonycore.bootstrap import bootstrapped_container
from databricksbundle.storage.StorageConfigurator import StorageConfigurator


class StorageConfiguratorTest(unittest.TestCase):
    def test_azure(self):
        container = bootstrapped_container.init("test_azure")
        storage_configurator: StorageConfigurator = container.get(StorageConfigurator)

        all_config = storage_configurator.get_config()

        self.assertEqual("tenant/123456", all_config["testing.storage.aaa"])
        self.assertEqual("secrets/some_client_id_scope1/some_client_id_key1", all_config["testing.secrets.aaa.client_id"])
        self.assertEqual("secrets/some_client_secret_scope1/some_client_secret_key1", all_config["testing.secrets.aaa.client_secret"])

        self.assertEqual("tenant/987654", all_config["testing.storage.bbb"])
        self.assertEqual("secrets/some_client_id_scope2/some_client_id_key2", all_config["testing.secrets.bbb.client_id"])
        self.assertEqual("secrets/some_client_secret_scope2/some_client_secret_key2", all_config["testing.secrets.bbb.client_secret"])


if __name__ == "__main__":
    unittest.main()
