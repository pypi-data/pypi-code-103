import boto3
from botocore.exceptions import ClientError
import json
def run():
    try:  
        bucket_name = input("Enter your buckets name: ")

        client = boto3.client('s3')
        policy = client.get_bucket_policy(Bucket=bucket_name)["Policy"]
        print(json.dumps(policy, sort_keys=True, indent=4))
    except ClientError as e:
        print(e)