import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')
vid = input("Please provide id of volume you want to delete: ")

def run():
    try:
        ec2.delete_volume( VolumeId=vid)
        print(f'{vid} deleted.')
    except ClientError as e:
        print(e)
                