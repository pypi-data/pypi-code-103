# -*- coding=utf-8

from qcloud_cos import CosS3Client, CosConfig

class GossTencentCOSClient(object):

    def __init__(self, secret_id, secret_key, region, bucket):
        """
        Initialize client
        """
        self._region = region
        self._bucket = bucket
        self._conf = CosConfig(
            Secret_id=secret_id,
            Secret_key=secret_key,
            Region=region,
            Scheme='https',
        )
        self._client = CosS3Client(
            conf=self._conf,
            retry=3,
        )

    def _get_object_url(self, key):
        """
        Get object URL from cloude
        """
        return self._conf.uri(bucket=self._bucket, path=key)

    def _list_objects(self, prefix):
        """
        List objects from cloude
        """
        try:
            resp = self._client.list_objects(Bucket=self._bucket, Prefix=prefix)
            return [item['Key'] for item in resp['Contents']]
        except:
            return []

    def _check_object(self, key):
        """
        Check object exists from cloude
        """
        try:
            result = self._client.object_exists(Bucket=self._bucket, Key=key)
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
            self._client.upload_file(Bucket=self._bucket, Key=key, LocalFilePath=local_path)
        except Exception as err:
            return '', err
        return self._get_object_url(key), None

    def _delete_object(self, key):
        """
        Delete object from cloude
        """
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)
        except:
            return False
        return True