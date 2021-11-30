import boto3
from botocore.exceptions import ClientError

def run():
    try:
        bucket_name=input("Please enter name of your bucket: ")
        key = input("Please enter key of your file.")
        client = boto3.client('s3')
        response = client.delete_object(Bucket=bucket_name , Key=key)
        print(response)
        print(f"Object {key} deleted!")
    except ClientError as e:
        print(e)

