import boto3
from botocore.exceptions import ClientError
client = boto3.client('s3')
bucet_name = input("Please enter name of your bucket")

def run():
    try:
        def counter():
            n = 0
            while True:
                n += 1
                yield n

        m = counter()
        objects = client.list_objects(Bucket=bucet_name)["Contents"]
        for object in objects:
            print(next(m),'.', object["Key"])
            print(object["LastModified"] , '<--Last Modified')
            print(object["Size"] , "<--Object size\n")
    except ClientError as e:
        print(e)