# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['aa_validator', 'py']
install_requires = \
['boto3>=1.20.17,<2.0.0',
 'pydash>=5.0.2,<6.0.0',
 'typing-extensions>=3.10,<5.0']

entry_points = \
{'console_scripts': ['aws-access-analyzer-validator = aa_validator:main']}

setup_kwargs = {
    'name': 'aws-access-analyzer-validator',
    'version': '0.2.0',
    'description': 'A tool to validate existing identity and resource policies across regions and supported AWS services with AWS IAM Access Analyzer.',
    'long_description': '# aws-access-analyzer-validator\n\nA tool to validate existing identity and resource policies across regions\nand supported AWS services with AWS IAM Access Analyzer.\n\nThis tool\n* discovers resource and identity policies attached to resources of supported\n  AWS services (see below) in all commercial regions\n* validates these policies with AWS IAM Access Analyzer [ValidatePolicy](https://docs.aws.amazon.com/access-analyzer/latest/APIReference/API_ValidatePolicy.html)\n  API\n* generates a report with Access Analyzer findings\n\nSee [examples/sample_report.md](examples/sample_report.md) for an example.\n\n## Usage\n\n1. Install from PyPI:\n\n  ```\n  pip install aws-access-analyzer-validator\n  ```\n\n2. Execute the tool:\n\n  ```\n  aws-access-analyzer-validator -o report.md\n  ```\n\n3. Open `report.md` to see analysis results.\n\n### Arguments\n\n`aws-access-analyzer-validator` supports the following arguments:\n\n* `--regions` - A comma separated list of regions to limit policy\n  validation to. For example, `--regions eu-west-1,eu-north-1` limits\n  validation to policies in `eu-west-1` and `eu-north-1` regions. Global\n  resources (IAM, S3) are scanned regardless of region limitations.\n\n### Supported Services / Resources\n\n`aws-access-analyzer-validator` validates policies from the following\nservices:\n\n* AWS Identity and Access Management (IAM)\n  * Inline policies of IAM users\n  * Inline policies of IAM groups\n  * Inline policies and trust policy of IAM roles\n  * Managed IAM Policies (customer managed)\n* Amazon S3 bucket policies\n* Amazon SQS queue policies\n* Amazon SNS topic policies\n\n### Required Permissions\n\nThis tool requires the following permissions to operate:\n\n* `accessanalyzer:ValidatePolicy`\n* `iam:GetAccountAuthorizationDetails`\n* `s3:GetBucketPolicy`\n* `s3:ListAllMyBuckets`\n* `sns:GetTopicAttributes`\n* `sns:ListTopics`\n* `sqs:GetQueueAttributes`\n* `sqs:ListQueues`\n\nHere\'s an IAM policy that grants the required privileges:\n\n```json\n{\n    "Version": "2012-10-17",\n    "Statement": [\n        {\n            "Sid": "PermissionsForAAValidator",\n            "Effect": "Allow",\n            "Action": [\n                "access-analyzer:ValidatePolicy",\n                "iam:GetAccountAuthorizationDetails",\n                "s3:GetBucketPolicy",\n                "s3:ListAllMyBuckets",\n                "sns:GetTopicAttributes",\n                "sns:ListTopics",\n                "sqs:GetQueueAttributes",\n                "sqs:ListQueues"\n            ],\n            "Resource": "*"\n        }\n    ]\n}\n```\n\n## Development\n\nRequires Python 3 and Poetry. Useful commands:\n\n```bash\n# Run integration tests (requires admin-level AWS credentials)\npoetry run tox -e test\n\n# Run linters\npoetry run tox -e lint\n\n# Format code\npoetry run tox -e format\n\n# Deploy test resources (requires AWS CLI and admin level AWS credentials)\nmake deploy-test-resources\n```\n\n## Credits\n\n* Inspired by [z0ph/aa-policy-validator](https://github.com/z0ph/aa-policy-validator).\n\n## License\n\nMIT.\n',
    'author': 'Sami Jaktholm',
    'author_email': 'sjakthol@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
