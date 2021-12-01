import boto3
import time
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')
ec22 = boto3.client('ec2')

def run():
    try:
        id = input('Please provide id for instance you want to modify: ')
        new_type = input('Please provide new type for your instance: ')
        instance = ec2.Instance(id)
        if instance.state['Name'] == 'running':
            ec2.instances.filter(InstanceIds = id).stop()
            time.sleep(60)
            ec22.modify_instance_attribute(InstanceId=id,
                                                    InstanceType={
                                                            'Value': new_type
                                                            })
            print(f'Type of instance: {id} is changed to {new_type}')
            
        else:
            ec22.modify_instance_attribute(InstanceId=id,
                                                    InstanceType={
                                                            'Value': new_type
                                                            })
            print(f'Type of instance: {id} is changed to {new_type}')
    except ClientError as e:
        print(e)
                