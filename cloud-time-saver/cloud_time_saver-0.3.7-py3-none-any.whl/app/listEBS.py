import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')

def run():
    try:
        fil_tag={"Name":"status","Values":['in-use']}
        print('Volumes in use: ')
        for each_vol in ec2.volumes.filter(Filters=[fil_tag]):
            print(f'Id: {each_vol.id} , size: {each_vol.size} \n')

        fil_tag2={"Name":"status","Values":['available']}
        print('Volumes available and not attached: ')
        for each_vol in ec2.volumes.filter(Filters=[fil_tag2]):
            print(f'Id: {each_vol.id} , size: {each_vol.size} \n')
        
        
    except ClientError as e:
        print(e)
                