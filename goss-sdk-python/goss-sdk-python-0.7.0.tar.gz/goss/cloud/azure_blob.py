from azure.storage.blob import BlobServiceClient


class GossAzureBlobClient(object):

    def __init__(self, secret_id, secret_key, region, bucket):
        self._client = BlobServiceClient.from_connection_string(conn_str=secret_id)
        self._bucket = bucket

    def _blob_client(self, container_name, blob_name):
        return self._client.get_blob_client(container_name, blob_name)

    def _get_object_url(self, key):
        """
        Get object URL from azure cloud
        """
        return self._blob_client(self._bucket, key).url

    def _upload_object(self, local_path, key):
        """
        Upload object to azure cloud
        """
        blob_client = self._blob_client(self._bucket, key)
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data)

    def _list_objects(self, prefix):
        """
        List objects from cloud
        """
        return []

    def _check_object(self, key):
        """
        Check object exists from cloude
        """
        try:
            return self._get_object_url(key), True
            raise
        except Exception:
            return '', False

    def _delete_object(self, key):
        """
        Delete object from azure cloud
        """
        blob_client = self._blob_client(self._bucket, key)
        try:
            blob_client.delete_blob()
            return True
        except Exception:
            return False
