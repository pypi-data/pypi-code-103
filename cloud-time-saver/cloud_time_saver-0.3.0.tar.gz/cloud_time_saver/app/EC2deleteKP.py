import boto3
from botocore.exceptions import ClientError
import os
import io

ec2 = boto3.client('ec2')

def run():
    try:
        key_name = input('Please provide name of key that you want to delete.')
        ec2.delete_key_pair(KeyName=key_name)
        print(f'{key_name} key deleted.')

    except ClientError as e:
        print(e)
                