# -*- coding=utf-8

from obs import ObsClient

class GossHuaweicloudOBSClient(object):

    def __init__(self, secret_id, secret_key, region, bucket):
        """
        Initialize client
        """
        self._region = region
        self._bucket = bucket
        self._client = ObsClient(
            access_key_id=secret_id,
            secret_access_key=secret_key,
            server='https://obs.{region}.myhuaweicloud.com'.format(region=region),
        )

    def _get_object_url(self, key):
        """
        Get object URL from cloude
        """
        return self._client.calling_format.get_full_url(self._client.is_secure, self._client.server, self._client.port, self._bucket, key, {})

    def _list_objects(self, prefix):
        """
        List objects from cloude
        """
        try:
            resp = self._client.listObjects(bucketName=self._bucket, prefix=prefix)
            return [item['key'] for item in resp['body']['contents']]
        except:
            return []

    def _check_object(self, key):
        """
        Check object exists from cloude
        """
        try:
            resp = self._client.getObject(bucketName=self._bucket, objectKey=key)
            if resp.status < 300:
                return self._get_object_url(key), True 
            raise
        except:
            return '', False

    def _upload_object(self, local_path, key):
        """
        Upload object to cloude
        """
        try:
            resp = self._client.putFile(bucketName=self._bucket, objectKey=key, file_path=local_path)
            if resp.status > 300:
                raise ValueError('Upload file error: {err}'.format(err=resp.errorMessage))
        except Exception as err:
            return '', err
        return resp.body['objectUrl'], None

    def _delete_object(self, key):
        """
        Delete object from cloude
        """
        try:
            resp = self._client.deleteObject(bucketName=self._bucket, objectKey=key)
            if resp.status > 300:
                raise
        except:
            return False
        return True