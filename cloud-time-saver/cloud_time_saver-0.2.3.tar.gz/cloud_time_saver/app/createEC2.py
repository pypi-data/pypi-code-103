import boto3
from botocore.exceptions import ClientError

resource = boto3.resource('ec2')

def run():
    instance_type = input("Enter type of instance: ")
    id = input("Choose ami(enter ami id): \n1.Amazon Linux 2 AMI=ami-02e136e904f3da870, \n2.macOS Big Sur 11.6=ami-0a3e62d0ab0b19c0f , \n3.Red Hat Enterprise Linux 8 (HVM), SSD Volume Type=ami-0b0af3577fe5e3532, \n4.SUSE Linux Enterprise Server 15 SP2 (HVM), SSD Volume Type=ami-0fde50fcbcd46f2f7 , \n5.Ubuntu Server 20.04 LTS (HVM), SSD Volume Type=ami-09e67e426f25ce0d7 , \n6.Microsoft Windows Server 2019 Base=ami-0416f96ae3d1a3f29, \n7.Debian 10 (HVM), SSD Volume Type=ami-07d02ee1eeb0c996c \n:")
    image_id = id
    try:
        response = resource.create_instances(ImageId= image_id , InstanceType = instance_type , MaxCount = 1 , MinCount = 1 )
        print(response , "created.")
    except ClientError as e:
        print(e)
                