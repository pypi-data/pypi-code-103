import boto3
from botocore.exceptions import ClientError
import io
import os

resource = boto3.resource('ec2')
ec2 = boto3.client('ec2')

def run():
    key_name = input('Please provide name for KeyPair for your EC2-instance: ')
    key_storage = input('Please provide full path to directory that will be used to store your key pair: ')
    os.chdir(key_storage)
    key_pair = resource.create_key_pair(KeyName=key_name)
    key_value = key_pair.key_material
    with io.open(key_name + '.pem' , "w" , encoding="utf-8") as key:
        key.write(str(key_value))
        key.close()
    
    group_name = input("Please enter name of security group that will be associated with this instance: ")
    security_group = resource.create_security_group(Description="Security group associated with ec2 instance created with cloud_time_saver",
                                                GroupName=group_name)
    response = ec2.describe_security_groups(
    Filters=[
        dict(Name='group-name', Values=[group_name])
    ]
)
    group_id = response['SecurityGroups'][0]['GroupId']
    

    ec2.authorize_security_group_ingress(
      GroupId=group_id,
      IpPermissions=[
          {
              'FromPort': 22,
              'IpProtocol': '-1',
              'IpRanges': [
                  {
                      'CidrIp': '0.0.0.0/0',
                      
                  },
              ],
              'ToPort': 22,
          }
      ]
              )
    instance_type = input("Enter type of instance ( e.g. t2.micro , t3.nano... ): ")
    id = input("Choose ami(enter ami id): \n1.Amazon Linux 2 AMI=ami-02e136e904f3da870, \n2.macOS Big Sur 11.6=ami-0a3e62d0ab0b19c0f , \n3.Red Hat Enterprise Linux 8 (HVM), SSD Volume Type=ami-0b0af3577fe5e3532, \n4.SUSE Linux Enterprise Server 15 SP2 (HVM), SSD Volume Type=ami-0fde50fcbcd46f2f7 , \n5.Ubuntu Server 20.04 LTS (HVM), SSD Volume Type=ami-09e67e426f25ce0d7 , \n6.Microsoft Windows Server 2019 Base=ami-0416f96ae3d1a3f29, \n7.Debian 10 (HVM), SSD Volume Type=ami-07d02ee1eeb0c996c \n:")
    image_id = id
    try:
        response = resource.create_instances(ImageId= image_id, 
                                            InstanceType = instance_type, 
                                            MaxCount = 1, 
                                            MinCount = 1,
                                            SecurityGroupIds = [
                                                group_id
                                            ]
                                            )
        print(response , "created.")
    except ClientError as e:
        print(e)