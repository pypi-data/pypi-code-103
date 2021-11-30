import boto3
from botocore.exceptions import ClientError


def run():
    client = boto3.client('ec2')
    security_group_id = input("Please enter security gtoup id: ")
    port = input("Please enter port number: ")

    try:
        data = client.revoke_security_group_egress(
                    GroupId=security_group_id,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                        'FromPort': int(port),
                        'ToPort': int(port),
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                        ])
        print('Rule Successfully removed %s' % data)
    except ClientError as e:
        print(e)