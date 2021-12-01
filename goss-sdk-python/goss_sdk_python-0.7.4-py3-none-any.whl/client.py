# -*- coding=utf-8

import os

import boto3 as amazon_s3
import qcloud_cos as tencent_cos
import oss2 as aliyun_oss
import obs as huaweicloud_obs

from .exception import GossException
from .comm import *
from .cloud import *


class GossClient(object):

    CLIENT_SUPPORTED_MAP = {
        GOSS_AMAZON_S3: GossAmazonS3Client,
        GOSS_TENCENT_COS: GossTencentCOSClient,
        GOSS_ALIYUN_OSS: GossAliyunOSSClient,
        GOSS_HUAWEICLOUD_OBS: GossHuaweicloudOBSClient,
        GOSS_AZURE_BLOB: GossAzureBlobClient,
    }
    
    def __init__(self, ctype, secret_id, secret_key, region, bucket):
        """
        Initialize client
        """
        if ctype not in self.CLIENT_SUPPORTED_MAP:
            raise GossException("OOS type about '{type}' does not supported".format_exc(type=ctype))
        self._client = self.CLIENT_SUPPORTED_MAP[ctype](secret_id, secret_key, region, bucket)

    def check_object(self, cloud_path):
        """
        Check object exists from cloude
        """
        return self._client._check_object(cloud_path)

    def list_objects(self, prefix=''):
        """
        List objects from cloude
        """
        return self._client._list_objects(prefix)

    def upload_object(self, local_path, cloud_path):
        """
        Upload object to cloude
        """
        if not os.path.exists(local_path):
            return '', 'File `{file}` does not exist'.format(file=local_path)
        return self._client._upload_object(local_path, cloud_path)

    def upload_file(self, local_path, cloud_path):
        """
        Old update object function
        """
        return self.upload_object(local_path, cloud_path)

    def delete_object(self, cloud_path):
        """
        Upload file to cloude
        """
        return self._client._delete_object(cloud_path)