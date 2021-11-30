import boto3
from botocore.exceptions import ClientError

client = boto3.client('ec2')

def run():
    group_id = input("Enter id of security group you want to delete: ")
    try:
        response = client.delete_security_group(GroupId=group_id)
        print('Security Group deleted %s .' % (group_id))

        
    except ClientError as e:
        print(e)