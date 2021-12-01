import boto3
import sys
import re
import click
import time
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')

lst = []
n = int(input('Enter number of instances you want to terminate: '))

for i in range(0,n):
    id = input('Provide ID: ')
    lst.append(id)

def run():
    try:
        ec2.instances.filter(InstanceIds = lst).stop()
        print('Successful')
    except ClientError as e:
        print(e)
                