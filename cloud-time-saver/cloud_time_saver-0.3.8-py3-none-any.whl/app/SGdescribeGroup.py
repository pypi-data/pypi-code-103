import boto3
import json
from botocore.exceptions import ClientError

def run():
    try:
        group_id = input("Please enter ID of group you want to describe: ")
        client = boto3.client('ec2')
        response = client.describe_security_groups(GroupIds=[group_id])
        print(json.dumps(response, sort_keys=True, indent=4))
    except ClientError as e:
        print(e)