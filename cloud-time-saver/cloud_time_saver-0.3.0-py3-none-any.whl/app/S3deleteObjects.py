import boto3
from botocore.exceptions import ClientError

def run():
    try:
        def counter():
            n = 0
            while True:
                n += 1
                yield n

        m = counter()

        client = boto3.client('s3')
        bucket_name=input("Please enter name of your bucket: ")

        objects = client.list_objects(Bucket=bucket_name)["Contents"]
        for object in objects:
            print("======================================================")
            client.delete_object(Bucket=bucket_name , Key = object["Key"])
            name = object["Key"]
            print(next(m) , "." , name , "Deleted")
            print(object["Size"] , "<-- Object size") 
            print("======================================================")
    except ClientError as e:
        print(e)