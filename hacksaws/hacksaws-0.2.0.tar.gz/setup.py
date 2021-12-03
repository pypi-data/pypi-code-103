# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hacksaws']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.16.0,<2.0.0']

entry_points = \
{'console_scripts': ['hacksaws = hacksaws:main']}

setup_kwargs = {
    'name': 'hacksaws',
    'version': '0.2.0',
    'description': 'A command line utility for AWS profiles using dynamic authentication methods such as MFA. ',
    'long_description': '# hacksaws\n\n[![PyPI version](https://badge.fury.io/py/hacksaws.svg)](https://badge.fury.io/py/hacksaws)\n[![build status](https://gitlab.com/rocket-boosters/hacksaws/badges/main/pipeline.svg)](https://gitlab.com/rocket-boosters/hacksaws/commits/main)\n[![coverage report](https://gitlab.com/rocket-boosters/hacksaws/badges/main/coverage.svg)](https://gitlab.com/rocket-boosters/hacksaws/commits/main)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-white)](https://gitlab.com/pycqa/flake8)\n[![Code style: mypy](https://img.shields.io/badge/code%20style-mypy-white)](http://mypy-lang.org/)\n[![PyPI - License](https://img.shields.io/pypi/l/hacksaws)](https://pypi.org/project/hacksaws/)\n\nA command line utility for AWS profiles using dynamic authentication \nmethods such as MFA. The CLI allows for dynamic logins to update\nthe credentials for an AWS profile temporarily, while storing the\nlong-term access key and secret in a backup file until the next\nlogin or logout call is made. That way dynamic logins can be used while\nstill maintaining the same functional credential interface as\nnon-dynamic credentials.\n\nAt this time only MFA-based dynamic logins are supported, but SSO\nand others will be added in the future.\n\n## Usage\n\nTo login with MFA, execute the command:\n\n```shell script\n$ hacksaws mfa login <PROFILE_NAME> <MFA_CODE>\n```\n\nThere is a `--lifespan` flag that can be appended here to adjust\nthe amount of time the profile login is valid for before it expires.\nThe default is 12 hours (`--lifetime=43200` seconds), but that can\nbe adjusted to a maximum of 24 hours if the profile login allows\nauthentication lifespans of that length.\n\nECR logins with docker can also be handled with the command by adding the `--ecr`\nflag. This will the local docker environment into ECR in the default AWS region for\nthe specified profile.\n\n```shell script\n$ hacksaws mfa login <PROFILE_NAME> <MFA_CODE> --ecr\n```\n\nIt is also possible to login to ECR in multiple regions with the `--ecr-region` flag.\n\n```shell script\n$ hacksaws mfa login <PROFILE_NAME> <MFA_CODE> \\\n    --ecr \\\n    --ecr-region=eu-central-1 \\\n    --ecr-region=us-west-2 \\\n    --ecr-region=ca-central-1\n```\n\nECR will always log into the AWS default region. The `--ecr-region` flag allows for\nadding additional regions to the login command.\n\nThen to log out:\n\n```shell script\n$ hacksaws mfa logout <PROFILE_NAME>\n```\n\nIt is possible to log in and out of ECR for the account with that\nprofile as well by including the `--ecr` flag in the login call.\n\nAlternate directories for the AWS credentials directory can be\nspecified with the `--directory` flag. \n\nAnd for separated AWS credentials directories in the home directory\nthat follow the pattern `~/.aws-<NAME>`, a `--name` flag can be\nspecified to use that directory instead of the default `~/.aws`\ndirectory. This is a useful pattern for separating profiles by\naccount in cases where one has multiple account credentials.\n\n## Requiring MFA\n\nHere\'s an example policy that allows a user to manage their own\nuser account settings while requiring MFA.\n\n```json\n{\n  "Version": "2012-10-17",\n  "Statement": [\n    {\n      "Sid": "ViewAccountInfo",\n      "Effect": "Allow",\n      "Action": [\n        "iam:ListUsers",\n        "iam:ListAccount*",\n        "iam:ListMFADevices",\n        "iam:GetAccountPasswordPolicy",\n        "iam:GetAccountSummary"\n      ],\n      "Resource": "*"\n    },\n    {\n      "Sid": "ViewAndManageTheirUser",\n      "Effect": "Allow",\n      "Action": [\n        "iam:*LoginProfile",\n        "iam:*AccessKey*",\n        "iam:*SSHPublicKey*",\n        "iam:*SigningCertificate*",\n        "iam:*ServiceSpecificCredential*",\n        "iam:GetUser",\n        "iam:ChangePassword"\n      ],\n      "Resource": "arn:aws:iam::*:user/${aws:username}"\n    },\n    {\n      "Sid": "ManageTheirOwnMFA",\n      "Effect": "Allow",\n      "Action": [\n        "iam:CreateVirtualMFADevice",\n        "iam:DeactivateMFADevice",\n        "iam:DeleteVirtualMFADevice",\n        "iam:EnableMFADevice",\n        "iam:ListMFADevices",\n        "iam:ListVirtualMFADevices",\n        "iam:ResyncMFADevice"\n      ],\n      "Resource": [\n        "arn:aws:iam::*:mfa/${aws:username}",\n        "arn:aws:iam::*:user/${aws:username}"\n      ]\n    },\n    {\n      "Sid": "DenyAllExceptListedIfNoMFA",\n      "Effect": "Deny",\n      "NotAction": [\n        "iam:ListUsers",\n        "iam:ListMFADevices",\n        "iam:ChangePassword",\n        "iam:GetUser",\n        "iam:CreateVirtualMFADevice",\n        "iam:EnableMFADevice",\n        "iam:ListMFADevices",\n        "iam:ListVirtualMFADevices",\n        "iam:ResyncMFADevice",\n        "sts:GetSessionToken"\n      ],\n      "Resource": "*",\n      "Condition": {\n        "BoolIfExists": {\n          "aws:MultiFactorAuthPresent": "false"\n        }\n      }\n    }\n  ]\n}\n```\n\nControlling password quality and expiration policies is an account-level requirement\nand more details can be found at\n(Setting an account password policy for IAM users)[https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_passwords_account-policy.html]\n\nAdditional Resources:\n\n- [Allows MFA-authenticated IAM users...](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_aws_my-sec-creds-self-manage-mfa-only.html)\n- [IAM: Allows IAM users to self-manage an MFA device](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_iam_mfa-selfmanage.html)\n- [Configuring MFA-protected API access](https://docs.amazonaws.cn/en_us/IAM/latest/UserGuide/id_credentials_mfa_configure-api-require.html)\n',
    'author': 'Scott Ernst',
    'author_email': 'swernst@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/rocket-boosters/hacksaws',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<4.0.0',
}


setup(**setup_kwargs)
