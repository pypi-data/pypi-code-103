from sys import stderr
from pathlib import Path
from toml import loads
from .clients.default_client import DefaultClient
from .clients.local_file_client import LocalFileClient

try:
    from .clients.es_client import EsClient
except ImportError as e:
    print("Did you forget to install `pip install pytest-db[es]`?", file=stderr)
    raise


class ClientFactory:
    def __init__(self, config_file):
        """
        Args:
            config_file (str): config file path
        """
        try:
            self.config = loads(Path(config_file).read_text())
        except FileNotFoundError:
            self.config = None

    def get_client(self):
        if not self.config:
            return DefaultClient(self.config)
        else:
            raise_upon_failure = self.config.get("raise-upon-failure", False)

            if self.config["type"] == "local":
                return LocalFileClient(
                    self.config, raise_upon_failure=raise_upon_failure
                )
            if self.config["type"] == "es":
                url = self.config["url"]
                index = self.config["index"]
                return EsClient(
                    self.config, url, index, raise_upon_failure=raise_upon_failure
                )
