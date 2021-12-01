import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')
iid = input('Please provide id of instance you want to detach volume from: ')
vid = input('Please provide id of volume you want to be detached from above instance: ')

def run():
    try:
        deatach_response=ec2.detach_volume(Device='/dev/xvdb',
                    InstanceId=iid,
                    VolumeId=vid
     )
        print(f'Volume {vid} detached from instance {iid}')
    except ClientError as e:
        print(e)
                