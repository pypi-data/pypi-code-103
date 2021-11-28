import boto3
from botocore.exceptions import ClientError

client = boto3.client('ec2')
def run():
    try:
        vpc_id=input("Enter id for VPC you want to delete: ")
    
        response = client.delete_vpc(VpcId=vpc_id)
        print(vpc_id , "Succesfully deleted")
        print(response)
    except ClientError as e:
        print(e)