import boto3
import sys
import re
import click
import time
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')

def run():
    try:
        instance_id = input('Please provide instance_id: ')
        myec2 = ec2.describe_instances(InstanceIds=[instance_id])
        template = r'^i'
        if re.search(template,instance_id):
            print('Succesfull id')
            def stop_start_instance():
                try:
                    ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
                except ClientError as e:
                        if 'DryRunOperation' not in str(e):
                            raise
                try:
                    response = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
                    print(response)
                except ClientError as e:
                    print(e)

                time.sleep(60)
    
                try:
                    ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
                except ClientError as e:
                    if 'DryRunOperation' not in str(e):
                        raise

                try:
                    response = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
                    print(response)
                except ClientError as e:
                    print(e)

        
            def report_state():
                try:
                    for pythonins in myec2['Reservations']:
                        for printout in pythonins['Instances']:
                            instance_state = (printout['State']['Name'])
                            while instance_state != 'running':
                                print("Instance state not yet running. Wait...")
                                time.sleep(20)
                            print('Your instance is again in running state')

                except ClientError as e:
                    print(e)
            
            stop_start_instance()
            report_state()

        else:
            print('Choose right id')
            sys.exit()
    
    except ClientError as e:
        print(e)
                