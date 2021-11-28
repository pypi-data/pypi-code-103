import boto3
from botocore.exceptions import ClientError
import glob
def run():
    try:
        client = boto3.client('s3')
        bucket_name = input("Please enter name of your bucket.")
        file_type =input("Please enter right type of your file (example= txt , png , jpeg , pdf): ")
        full_path = input("Please enter full path to your directory.")

        if file_type == 'txt':
            files = glob.glob(full_path+"/*.txt")
            for file in files:
                client.upload_file(Filename=file , Bucket=bucket_name, Key=file.split("/")[-1])
        elif file_type == 'png':
            files = glob.glob(full_path+"/*.png")
            for file in files:
                client.upload_file(Filename=file , Bucket=bucket_name, Key=file.split("/")[-1])
        elif file_type == '.jpeg':
            files = glob.glob(full_path+"/*.jpeg")
            for file in files:
                client.upload_file(Filename=file , Bucket=bucket_name, Key=file.split("/")[-1])
        elif file_type == '.pdf':
            files = glob.glob(full_path+"/*.pdf")
            for file in files:
                client.upload_file(Filename=file , Bucket=bucket_name, Key=file.split("/")[-1])
        else:
            print("We dont support that kind of format.")
        
            
    except ClientError as e:
        print(e)