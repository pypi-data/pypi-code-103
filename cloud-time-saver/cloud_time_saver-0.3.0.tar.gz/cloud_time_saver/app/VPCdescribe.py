import boto3
from botocore.exceptions import ClientError
import json

client = boto3.client('ec2')
vpc_id = input("Enter id of VPC you want to describe: ")
def run():
    try:
        response = client.describe_vpcs(
            VpcIds=[
                vpc_id,
            ],
    )
        print(json.dumps(response, sort_keys=True, indent=4))
    except ClientError as e:
        print(e)
