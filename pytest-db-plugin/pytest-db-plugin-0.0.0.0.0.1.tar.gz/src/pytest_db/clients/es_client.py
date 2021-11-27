from elasticsearch import Elasticsearch
from .base_client import UrlClient, FailedUpload


class EsClient(UrlClient):
    """
    Uploads each document to a DB using a url (can also be a DB hosted on
    localhost)
    """

    def __init__(self, config, url, index, *, raise_upon_failure=False):
        super().__init__(config, url, raise_upon_failure=raise_upon_failure)
        self._index = index

    def connect(self):
        self._client = Elasticsearch(self._url)

    def _upload(self):
        result = self._client.index(
            index=self._index, document=self._data, doc_type="_doc"
        )
        if result.get("_shards").get("failed"):
            raise FailedUpload(result)
