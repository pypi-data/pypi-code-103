import boto3
from botocore.exceptions import ClientError

client = boto3.client('ec2')
def run():
    try:
        def counter():
            n = 0
            while True:
                n += 1
                yield n

        m = counter()
        response = client.describe_vpcs()
        for vpc in response["Vpcs"]:
            print(next(m), '.' , "Vpc id:", vpc["VpcId"])
            print("Cidr Block: " ,vpc["CidrBlock"])

    except ClientError as e:
        print(e)