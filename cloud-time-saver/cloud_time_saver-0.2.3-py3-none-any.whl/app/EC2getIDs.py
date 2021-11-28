import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')

def run():
    try:
        def counter():
            n = 0
            while True:
                n += 1
                yield n

        m = counter()

        print("Running instances:")
        instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            print(next(m),instance.id, instance.instance_type)

        print('\n')

        print("Stopped instances:")
        instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
        for instance in instances:
            print(next(m),instance.id, instance.instance_type)
        
        
    except ClientError as e:
        print(e)
                