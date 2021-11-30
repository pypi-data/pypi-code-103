import boto3
from botocore.exceptions import ClientError

client = boto3.client('ec2')

def run():
    vpc_id = input("Enter id of VPC you want to create Sec Group in: ")
    group_name = input("Enter name of your Sec Group: ")
    description = input("Enter description for group: ")

    try:
        response = client.create_security_group(GroupName=group_name,
                                            Description=description,
                                            VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

        
    except ClientError as e:
        print(e)