import numpy as np
import httpx

from qiniu import put_file, put_data, Auth, etag
from qiniu import BucketManager, build_batch_delete

from hamunafs.backends.base import BackendBase

class Qiniu(BackendBase):
    def __init__(self, cfg):
        key, secret, domain, default_bucket = cfg['key'], cfg['secret'], cfg['domain'], cfg['default_bucket']
        self.auth = Auth(key, secret)
        self.domain = domain
        self.default_bucket = default_bucket
        self.bucket = BucketManager(self.auth)
    
    def get_token(self, filename):
        return self.auth.upload_token(self.default_bucket, filename)
    
    def geturl(self, entrypoint):
        bucket, bucket_name = entrypoint.split('/')
        return 'http://{}/{}_{}'.format(self.domain, bucket, bucket_name)

    def put(self, file, bucket, bucket_name, tmp=True):
        try:
            if tmp:
                _bucket = 'tmp_file_' + bucket
            else:
                _bucket = bucket
            b_name = '{}_{}'.format(_bucket, bucket_name)
            token = self.auth.upload_token(self.default_bucket, b_name)
            ret, info = put_file(token, b_name, file)
            if ret is not None:
                return True, '{}/{}'.format(_bucket, bucket_name)
            return False, '上传失败'
        except Exception as e:
            return False, str(e)

    def put_buffer(self, buffer, bucket, bucket_name):
        try:
            b_name = '{}_{}'.format(bucket, bucket_name)
            token = self.auth.upload_token(self.default_bucket, b_name)
            ret, info = put_data(token, b_name, buffer)
            if ret is not None:
                return True, '{}/{}'.format(bucket, bucket_name)
            return False, '上传失败'
        except Exception as e:
            return False, str(e)

    def get(self, download_path, bucket, bucket_name, tries=0):
        try:
            if tries >= 3:
                return False, '下载出错'
            else:
                url = 'http://{}/{}'.format(self.domain, '{}_{}'.format(bucket, bucket_name))
                print(url)
                with open(download_path, mode='wb') as f:
                    with httpx.stream('GET', url) as response:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
                return True, download_path
        except Exception as e:
            if tries >= 3:
                return False, str(e)
            else:
                return self.get(download_path, bucket, bucket_name, tries+1)
            
