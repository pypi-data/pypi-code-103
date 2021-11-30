import boto3
from botocore.exceptions import ClientError
import os
import io

resource = boto3.resource('ec2')

def run():
    try:
        key_name = input('Please provide name for KeyPair for your EC2-instance: ')
        key_storage = input('Please provide full path to directory that will be used to store your key pair: ')
        os.chdir(key_storage)
        key_pair = resource.create_key_pair(KeyName=key_name)
        key_value = key_pair.key_material
        with io.open(key_name + '.pem' , "w" , encoding="utf-8") as key:
            key.write(str(key_value))
            key.close()
        print(f'{key_name} key created.')
        
    except ClientError as e:
        print(e)
                