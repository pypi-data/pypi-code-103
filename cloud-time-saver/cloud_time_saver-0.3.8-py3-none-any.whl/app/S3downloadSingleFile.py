import boto3
from botocore.exceptions import ClientError
import os

client = boto3.client('s3')

def run():
    try:
        bucket_name=input("Please enter name of your bucket: ")
        key = input("Please enter key of your file.")
        filename=input("Please sign  name to file that you want to download")

        
        full_path = input('Please provide correct full path to your current working directory')
        os.chdir(full_path)
        dir_name = input('Please provide name of directory that will be used t store downloaded data: ')
        os.mkdir(dir_name)
        cwd = full_path + '/' + dir_name
        os.chdir(cwd)

        client.download_file(Bucket=bucket_name , Key=key , Filename= filename )
        print(f"{key} is downloaded")
        print(f"{filename} is placed into your dir.")
    except ClientError as e:
        print(e)