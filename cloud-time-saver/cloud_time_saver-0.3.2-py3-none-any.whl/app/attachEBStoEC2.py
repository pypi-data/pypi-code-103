import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')
iid = input('Please provide id of instance you want to attach volume to: ')
vid = input('Please provide id of volume you want to be attached to above instance: ')

def run():
    try:
        attach_response=ec2.attach_volume(Device='/dev/xvdb',
                    InstanceId=iid,
                    VolumeId=vid
     )
        print(f'Volume {vid} attached to instance {iid}')
    except ClientError as e:
        print(e)
                