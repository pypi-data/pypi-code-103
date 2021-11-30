import boto3
import sys
import re
import click
import time
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')

id = input('Please provide id for instance you want to terminate: ')

def run():
    try:
        ec2.instances.filter(InstanceIds = id).terminate()
        print(f'Instance {id} terminated.')
    except ClientError as e:
        print(e)
                