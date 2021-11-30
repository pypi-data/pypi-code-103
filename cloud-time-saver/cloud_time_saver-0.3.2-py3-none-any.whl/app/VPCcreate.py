import boto3
from botocore.exceptions import ClientError

client = boto3.client('ec2')
def run():
    try:
        cidr_block=input("Please enter Cidr block: ")
    
        response = client.create_vpc(CidrBlock=cidr_block)
        print(response)
    except ClientError as e:
        print(e)