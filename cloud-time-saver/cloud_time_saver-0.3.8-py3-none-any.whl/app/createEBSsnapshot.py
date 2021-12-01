import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')
vid = input("Please provide id of volume you want to make snapshot from: ")
description = ("Provide description for your snapshot: ")

def run():
    try:
        ec2.create_snapshot( Description=description,
      VolumeId=vid)
        print(f'Snapshot created from volume {vid}')
    except ClientError as e:
        print(e)
                