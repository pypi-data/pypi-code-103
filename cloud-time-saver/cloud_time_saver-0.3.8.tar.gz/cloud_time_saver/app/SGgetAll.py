import boto3
import json
from botocore.exceptions import ClientError

def run():
    try:
        def counter():
            n = 0
            while True:
                n += 1
                yield n

        m = counter()
        client = boto3.client('ec2')
        groups = client.describe_security_groups()
        for group in groups["SecurityGroups"]:
            print(next(m), '.' ,group["GroupName"])
            print("Group ID: " ,group["GroupId"])
    except ClientError as e:
        print(e)
            
