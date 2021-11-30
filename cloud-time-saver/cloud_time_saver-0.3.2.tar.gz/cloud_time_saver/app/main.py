import fire
import importlib
import pkgutil
import logging
from colorama import Fore

def find_and_run_plugins(plugin_prefix):
    plugins={}
    print("Just a second")
    for _,name,_ in pkgutil.iter_modules():
        if name.startswith(plugin_prefix):
            module = importlib.import_module(name)
            plugins[name] = module
    for name, module in plugins.items():
        module.run()

def cheat_sheat():
    print(Fore.WHITE ,'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(Fore.BLUE , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ WELCOME TO HELP PAGE! ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(Fore.BLUE , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('                         HERE IS LIST OF SERVICES YOU CAN INTERACT WITH: ')
    print(Fore.GREEN , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('                         S3 \n','                        EC2 \n','                        Security Groups \n','                        VPC')
    print(Fore.GREEN , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(Fore.BLUE , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('                         HERE ARE COMMANDS YOU CAN RUN FOR SPECIFIC SERVICE:')
    print(Fore.YELLOW , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|')
    print(Fore.YELLOW, 'S3:                                                                                                                  |\n' ,
                         '1. S3createBucket       --> Creates S3 bucket.                                                                       |\n',
                         '2. S3deleteBucket       --> Deletes S3 bucket.                                                                       |\n' ,
                         '3. S3deleteObject       --> Deletes object from S3 bucket.                                                           |\n',
                         '4. S3deleteObjects      --> Deletes all objects from S3 bucket.                                                      |\n',
                         '5. S3deletePolicy       --> Deletes bucket Policy.                                                                   |\n',
                         '6. S3downloadSingleFile --> Downloads single file from bucket in root directory of program + /Scripts/download.      |\n',
                         '7. S3downloadAllFiles   --> Downloads all files from bucket in root directory of program + /Scripts/download.        |\n',
                         '8. S3listBuckets        --> List all bucket within your account.                                                     |\n',
                         '9. S3listObjects        --> List all objects within single bucket.                                                   |\n',
                         '10. S3listPolicy        --> List policy of single bucket.                                                            |\n',
                         '11. S3uploadSingleFile  --> Uploads single file from system to S3 bucket.                                            |\n',
                         '12. S3uploadDir         --> Uploads whole directory from system to S3 bucket.                                        |')
    print(Fore.YELLOW , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|')

    print(Fore.GREEN , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|')
    print(Fore.GREEN, 'VPC:                                                                                                                 |\n' ,
                         '1. VPCcreate       --> Creates VPC.                                                                                  |\n',
                         '2. VPCdelete       --> Deletes VPC.                                                                                  |\n' ,
                         '3. VPCdescribe     --> Provides you with description of your VPC.                                                    |\n',
                         '4. VPCgetID        --> Gets ID of your VPC.                                                                          |')
    print(Fore.GREEN , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|')

    print(Fore.CYAN , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|')
    print(Fore.CYAN, 'EC2:                                                                                                                 |\n' ,
                         '1. createEC2       --> Creates EC2 instance.                                                                         |',)
    print(Fore.CYAN , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|')

    print(Fore.MAGENTA , 'SECURITY GROUPS:                                                                                                     |\n' ,
                         '1. createGroup       --> Creates Security Group.                                                                     |\n',
                         '2. removeGroup       --> Removes Security Group                                                                      |\n',
                         '3. describeGroup     --> Describes Security group                                                                    |\n',
                         '4. getGroupID        --> Gets ID of every Security group                                                             |\n',
                         '5. addInboundRule    --> Adds one inbound rule to Security Group                                                     |\n',
                         '6. removeInboundRule --> Removes one inbound rule from Security Group                                                |\n',
                         '7. addOutboundRule   --> Adds one outbound rule to your Security Group                                               |\n',
                         '8.removeOutboundRule --> Removes one outbound rule from Security Group                                               |')
    print(Fore.MAGENTA , '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|')
if __name__=='__main__':
    fire.Fire()