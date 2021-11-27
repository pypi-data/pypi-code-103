import json
from tempfile import NamedTemporaryFile


from .base_client import DbClient


class LocalFileClient(DbClient):
    """
    Saves each test output to a document file under /tmp
    """

    def _upload(self):
        with NamedTemporaryFile(mode="w+", delete=False, suffix=".db") as f:
            self._logger.info(f"saving test data to local file ({f.name})")
            json.dump(self._data, f)
