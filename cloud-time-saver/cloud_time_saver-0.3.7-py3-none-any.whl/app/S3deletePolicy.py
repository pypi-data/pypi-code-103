import boto3
from botocore.exceptions import ClientError
client = boto3.client('s3')

def run():
    try:
        bucket_name = input("Please enter name of your bucket: ")
        response = client.delete_bucket_policy(Bucket=bucket_name)
        print(response)
    except ClientError as e:
        print(e)