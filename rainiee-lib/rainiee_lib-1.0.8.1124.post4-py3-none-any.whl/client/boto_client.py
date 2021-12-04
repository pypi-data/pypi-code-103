import traceback
import boto3
from io import StringIO
from botocore.exceptions import ClientError
from ..lib.utils import *


class BotoClient(object):
    def __init__(self):
        self.ACCESS_KEY = 'AKIAIWPNDYOM6HPUZTBQ'
        self.SECRET_KEY = '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'
        self.s3_client = boto3.client('s3', aws_access_key_id=self.ACCESS_KEY, aws_secret_access_key=self.SECRET_KEY)
        self.s3_resource = boto3.resource('s3', aws_access_key_id=self.ACCESS_KEY, aws_secret_access_key=self.SECRET_KEY)
        self.bucket = 'rainiee'

    def get_client(self):
        return self.s3_client

    def upload_to_aws(self, local_file, s3_file,delete_local_file = False):
        try:
            self.s3_client.upload_file(local_file, self.bucket, s3_file)
            info("Upload Successful")
            if delete_local_file:
                import os
                os.remove(local_file)
        except Exception as e:
            error(traceback.format_exc())
            return False
        return True

    def pandas_to_aws(self, dataframe, file_path, file_name = 'df.csv'):
        try:
            csv_buffer = StringIO()
            dataframe.to_csv(csv_buffer)
            self.s3_resource.Object(self.bucket, str(file_path)+str(file_name)).put(Body=csv_buffer.getvalue())
            info('Successfully uploaded to S3 to ' + str(file_path) + str(file_name))
            return True
        except Exception:
            error(traceback.format_exc())
            return False

    def contains_file(self, file_name):
        try:
            file_list = self.s3_client.list_objects(Bucket = self.bucket)['Contents']
            for file in file_list:
                if file_name in file['Key']:
                    info('Already containing S3 file ' + file_name)
                    return True
            return False
        except Exception:
            error(traceback.format_exc())
            return False

    def check_file_exist(self, file_path, file_name):
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=file_path+file_name)
        except ClientError as e:
            return int(e.response['Error']['Code']) != 404
        return True
