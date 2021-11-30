import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')

az = input('Please provide availlabillity zone you want to place your EBS volume to ( us-east-1a... ): ')
size = input('Please provide size that you want( Gb ): ')
volume_type = input('Enter type of your volume ( gp2, gp3, io1, io2...): ')
name = input('Enter name for your volume: ')

def run():
    try:
        ec2.create_volume(AvailabilityZone=az,
        Size=int(size),
        Encrypted=True,               
        VolumeType=volume_type,
        TagSpecifications=[
            {
                'ResourceType': 'volume',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': name
                    },
                ]
            },
        ],
        
    )
        print(f'Volume {name} created in AZ {az}')
    except ClientError as e:
        print(e)
                