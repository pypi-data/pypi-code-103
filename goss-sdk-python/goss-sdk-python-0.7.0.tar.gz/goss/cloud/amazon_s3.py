# -*- coding=utf-8

from boto3 import Session

class GossAmazonS3Client(object):

    RESOURCE_URI_FORMAT = 'https://{bucket}.s3-{region}.amazonaws.com/{path}'

    def __init__(self, secret_id, secret_key, region, bucket):
        """
        Initialize client
        """
        self._region = region
        self._bucket = bucket
        self._client = Session(
            aws_access_key_id=secret_id,
            aws_secret_access_key=secret_key,
            region_name=region,
        ).client('s3')

    def _get_object_url(self, key):
        """
        Get object URL from cloude
        """
        return self.RESOURCE_URI_FORMAT.format(bucket=self._bucket, region=self._region, path=key)

    def _list_objects(self, prefix):
        """
        List objects from cloude
        """
        try:
            resp = self._client.list_objects_v2(Bucket=self._bucket, Prefix=prefix)
            return [item['Key'] for item in resp['Contents']]
        except:
            return []

    def _check_object(self, key):
        """
        Check object exists from cloude
        """
        try:
            resp = self._client.get_object(Bucket=self._bucket, Key=key)
            if resp['ResponseMetadata']['HTTPStatusCode'] < 300:
                return self._get_object_url(key), True 
            raise
        except:
            return '', False

    def _upload_object(self, local_path, key):
        """
        Upload object to cloude
        """
        try:
            self._client.upload_file(Filename=local_path, Bucket=self._bucket, Key=key)
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