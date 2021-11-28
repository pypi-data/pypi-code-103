# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cloud_time_saver', 'cloud_time_saver.app']

package_data = \
{'': ['*']}

install_requires = \
['boto3==1.19.7', 'click==8.0.3', 'colorama==0.4.4', 'fire==0.4.0']

entry_points = \
{'console_scripts': ['cloud_time_saver = cloud_time_saver.cts:main']}

setup_kwargs = {
    'name': 'cloud-time-saver',
    'version': '0.2.3',
    'description': 'Python CLI tool that automates working on AWS enviorment without leaving the Terminal.',
    'long_description': '# cloud_time_saver\n\ncloud_time_saver is a python command-line application, that lets us control our AWS environment automatically without leaving the terminal.\nIt is designed to be used only on the Linux operating system.\n\n# Introduction\n\nThe goal of this application is to speed up and simplify working with AWS and thus save users a lot of time.\n\nIn addition, it personally never suited me to use the AWS CLI, so I decided to do something similar, only my application was adapted for easier understanding and use.\n\n# Installation steps\n\n## Preinstallation \nBefore installation please make sure that you have python3 installed.\n\nAfter that one more thing. For this program to work you must have AWS account configured on your system.\nIf you do not have a configured account, you must first install AWS CLI.\nThen create a new user in the AWS console. When done, run the AWS configure command and add credentials for the created user to it.\nOn Ubuntu OS that should look similar to this:\n```bash\n /* installing AWS CLI */\n\n sudo apt-get install awscli\n\n /* now create new user in AWS Console */\n\n /* running aws configure will prompt you for user credentials */\n\n aws configure\n```\n <sub><sup>If you get errors when running application regarding to your AWS User settings, you can run: pip3 install --upgrade awscli</sup></sub>\n\n## Installation\nNow when we are done with configuring our account we can install cloud_time_saver with this command:\n```bash\npip install cloud-time-saver\n```\nIf you want to run the cloud_time_saver command globally you should consider adding the installation directory to your PATH variable.\n\n\n# Options\nWhen you run cloud_time_saver you will have 3 options to choose from:\n1. run ( starts application )\n2. help ( provides you with documentation )\n3. exit ( exits application )\n\n## help\nI recommend running the help command first, and seeing what kind of commands we can run. At first glance, this app may be a bit confusing, but a good look at the documentation should resolve disagreements.\nThis is how the help page looks like:\n![image1](https://raw.githubusercontent.com/JaSamLudiMoskri/cloud_time_saver_prod/main/Screenshot%202021-11-27%20141217.png)\n\n![image2](https://raw.githubusercontent.com/JaSamLudiMoskri/cloud_time_saver_prod/main/Screenshot%202021-11-27%20141300.png)\n\n\n \n\n\n\n',
    'author': 'Marko Mandic',
    'author_email': 'mandicm223@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
