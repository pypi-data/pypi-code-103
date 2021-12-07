import botocore
import boto3
import time
import os



class Upload:

    def __init__(self, role):
        self.s3_client = self.get_s3_client(role)

    def delete_all_objects(self, bucket_name, ext=None):
        bucket = self.s3_client.Bucket(bucket_name)
        for file_on_s3 in bucket.objects.all():
            if ext and not file_on_s3.key.endswith(ext):
                continue
            print("deleteing %s " % file_on_s3.key)
            response = bucket.delete_objects(
                Delete={
                    'Objects': [
                        {
                            'Key': file_on_s3.key
                        },
                    ],
                    'Quiet': False
                })


    def upload_file(self, bucket_name, collection, path):
        if os.path.isdir(path):
            self._upload_folder(bucket_name, collection, path)
        else:
            self._upload_file(bucket_name, collection, path)

    def _upload_folder(self, bucket_name, collection, path):
        bucket = self.s3_client.Bucket(bucket_name)
        existing_files = {}
        for zip_on_s3 in bucket.objects.filter(Prefix=collection):
            existing_files[os.path.basename(zip_on_s3.key)] = zip_on_s3.size

        for root, dirs, files in os.walk(path):
            for f in files:
                doc_path = os.path.join(root, f)
                name = os.path.basename(doc_path)
                if name not in existing_files.keys():
                    print("Uploading new file: %s" % name)
                    self._upload_file(bucket_name, collection, doc_path)
                else:
                    size = os.path.getsize(doc_path)
                    if size != existing_files[name]:
                        print("Overwriting due to size change for file: %s" % name )
                        self._upload_file(bucket_name, collection, doc_path)
                    else:
                        print("Noting change for file: %s" % name)

    def _upload_file(self, bucket_name, collection, path):
        file_obj = self.s3_client.Object(bucket_name, '%s/%s' % (collection, os.path.basename(path)))
        if not path.endswith('.zip'):
            return
        with open(path, 'rb') as f:
            data = f.read()
        file_obj.put(Body=data)

    def get_s3_client(self, role):
        # create an STS client object that represents a live connection to the
        # STS service
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

        return s3_resource

