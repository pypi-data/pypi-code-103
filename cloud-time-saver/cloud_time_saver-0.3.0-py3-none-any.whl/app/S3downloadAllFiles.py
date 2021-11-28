import boto3
from botocore.exceptions import ClientError
import os

def run():
    try:
        full_path = input('Please provide correct full path to your current working directory')
        os.chdir(full_path)
        dir_name = input('Please provide name of directory that will be used t store downloaded data: ')
        os.mkdir(dir_name)
        cwd = full_path + '/' + dir_name
        os.chdir(cwd)
        bucket_name=input("Please enter name of your bucket: ")
        client = boto3.client('s3')

        objects = client.list_objects(Bucket=bucket_name)["Contents"]
        for object in objects:
            client.download_file(Bucket=bucket_name , Key=object["Key"] , Filename= object["Key"])
    except ClientError as e:
        print(e)