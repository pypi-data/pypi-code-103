import json

import boto3
from botocore.config import Config

from hca_util.settings import AWS_SECRET_NAME


class Aws:

    def __init__(self, user_profile):
        self.user_profile = user_profile
        self.common_session = self.new_session()
        self.is_contributor = False
        self.bucket_name = 'covid-utils-ui-88560523'

    def new_session(self):
        return boto3.Session(region_name=self.user_profile.region,
                             aws_access_key_id=self.user_profile.access_key,
                             aws_secret_access_key=self.user_profile.secret_key)

    def is_valid_credentials(self):
        """
        Validate user config/credentials by making a get_caller_identity aws api call
        :return:
        """
        s3 = self.common_session.client('s3', endpoint_url='https://uk1s3.embassy.ebi.ac.uk')

        try:
            s3.list_buckets()
            return True

        except Exception as e:
            return False

        '''print(sts.list_buckets())

        for key in sts.list_objects(Bucket='covid-utils-ui-88560523')['Contents']:
            print(key['Key'])'''

    def get_bucket_name(self):
        """
        Get bucket name from aws secrets
        :return:
        """
        # access policy can't be attached to a secret
        # GetSecretValue action should be allowed for user
        secret_mgr = self.common_session.client('secretsmanager')

        resp = secret_mgr.get_secret_value(SecretId=AWS_SECRET_NAME)
        secret_str = resp['SecretString']
        self.bucket_name = json.loads(secret_str)['s3-bucket']
        return self.bucket_name

    def obj_exists(self, key):
        """
        return true if key exists, else false
        A folder/directory is an s3 object with key <uuid>/
        Note: s3://my-bucket/folder != s3://my-bucket/folder/
        Refer to https://www.peterbe.com/plog/fastest-way-to-find-out-if-a-file-exists-in-s3
        for comparison between client.list_objects_v2 and client.head_object to make this check.
        Also check https://stackoverflow.com/questions/33842944/check-if-a-key-exists-in-a-bucket-in-s3-using-boto3
        which suggests using Object.load() - which does a HEAD request, however, HCAContributor doesn't have
        s3:GetObject permission by default, so this will fail for them.
        """
        response = self.new_session().client('s3', endpoint_url='https://uk1s3.embassy.ebi.ac.uk', config=Config(s3={'addressing_style': 'path'})).list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=key,
        )
        for obj in response.get('Contents', []):
            if obj['Key'] == key:
                return True
        return False
