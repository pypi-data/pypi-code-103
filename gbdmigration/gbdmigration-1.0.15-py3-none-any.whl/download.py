import botocore
import boto3
import time
import os

class Download:

    def __init__(self, role=None):
        self.done_archives = self.get_done_files()
        self.s3_client = self.get_s3_client(role)

    def get_done_files(self):
        done_archives = []
        if not os.path.exists('migration.done'):
            return []
        with open('migration.done', 'r') as f:
            for line in f.readlines():
                done_archives.append(line.replace('\n', ''))
        return done_archives

    def download_files(self, bucket_name, collection, path_to_dest):
        bucket = self.s3_client.Bucket(bucket_name)
        files_to_download = []
        for zip_on_s3 in bucket.objects.filter(Prefix=collection):
            if zip_on_s3.key in self.done_archives:
                continue
            files_to_download.append(zip_on_s3.key)
        for f in files_to_download:
            file_obj = self.s3_client.Object(bucket_name, f)
            dest_file = os.path.join(path_to_dest, f.replace('%s/' % collection, ''))
            print("Downloading %s to %s" % (f, dest_file))
            with open(dest_file, 'wb') as data:
                file_obj.download_fileobj(data)
            with open('migration.done', 'a') as done:
                done.write('%s\n'% f)


    def get_s3_client(self, role):
        # Use the temporary credentials that AssumeRole returns to make a
        # connection to Amazon S3
        if role:
            sts_client = boto3.client('sts')

            # Call the assume_role method of the STSConnection object and pass the role
            # ARN and a role session name.
            assumed_role_object = sts_client.assume_role(
                RoleArn=role,
                RoleSessionName="migration%s" % time.time()
            )

            # From the response that contains the assumed role, get the temporary
            # credentials that can be used to make subsequent API calls
            credentials = assumed_role_object['Credentials']

            # Use the temporary credentials that AssumeRole returns to make a
            # connection to Amazon S3
            s3_resource = boto3.resource(
                's3',
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
            )
        else:
            s3_resource = boto3.resource(
                's3'
            )
        return s3_resource

