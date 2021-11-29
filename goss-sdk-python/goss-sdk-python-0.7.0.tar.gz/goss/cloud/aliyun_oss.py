# -*- coding=utf-8

from oss2 import Auth, Bucket
from oss2.compat import urlunquote

class GossAliyunOSSClient(object):

    def __init__(self, secret_id, secret_key, region, bucket):
        """
        Initialize client
        """
        self._region = region
        self._bucket = bucket
        self._client = Bucket(
            auth=Auth(secret_id, secret_key),
            endpoint='https://{region}.aliyuncs.com'.format(region=region),
            bucket_name=bucket,
        )

    def _get_object_url(self, key):
        """
        Get object URL from cloude
        """
        return urlunquote(self._client._make_url(self._bucket, key))

    def _list_objects(self, prefix):
        """
        List objects from cloude
        """
        try:
            resp = self._client.list_objects(prefix=prefix)
            return [item.key for item in resp.object_list]
        except:
            return []

    def _check_object(self, key):
        """
        Check object exists from cloude
        """
        try:
            result =  self._client.object_exists(key=key)
            if result:
                return self._get_object_url(key), True
            raise
        except:
            return '', False

    def _upload_object(self, local_path, key):
        """
        Upload object to cloude
        """
        try:
            self._client.put_object_from_file(key=key, filename=local_path)
        except Exception as err:
            return '', err
        return self._get_object_url(key), None

    def _delete_object(self, key):
        """
        Delete object from cloude
        """
        try:
            result = self._client.delete_object(key=key)
            if result.status < 300:
                return True
            raise
        except:
            return False