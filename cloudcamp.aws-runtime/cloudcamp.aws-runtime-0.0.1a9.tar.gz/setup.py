import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cloudcamp.aws-runtime",
    "version": "0.0.1.a9",
    "description": "CloudCamp - Launch faster by building scalable infrastructure in few lines of code.",
    "license": "MIT",
    "url": "https://cloudcamphq.com",
    "long_description_content_type": "text/markdown",
    "author": "Markus Ecker<markus.ecker@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cloudcamphq/cloudcamp.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cloudcamp.aws_runtime",
        "cloudcamp.aws_runtime._jsii"
    ],
    "package_data": {
        "cloudcamp.aws_runtime._jsii": [
            "aws-runtime@0.0.1-alpha.9.jsii.tgz"
        ],
        "cloudcamp.aws_runtime": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-applicationautoscaling>=1.129.0, <2.0.0",
        "aws-cdk.aws-certificatemanager>=1.129.0, <2.0.0",
        "aws-cdk.aws-chatbot>=1.129.0, <2.0.0",
        "aws-cdk.aws-cloudwatch-actions>=1.129.0, <2.0.0",
        "aws-cdk.aws-cloudwatch>=1.129.0, <2.0.0",
        "aws-cdk.aws-codepipeline-actions>=1.129.0, <2.0.0",
        "aws-cdk.aws-codepipeline>=1.129.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.129.0, <2.0.0",
        "aws-cdk.aws-ecs-patterns>=1.129.0, <2.0.0",
        "aws-cdk.aws-ecs>=1.129.0, <2.0.0",
        "aws-cdk.aws-elasticloadbalancingv2>=1.129.0, <2.0.0",
        "aws-cdk.aws-logs>=1.129.0, <2.0.0",
        "aws-cdk.aws-rds>=1.129.0, <2.0.0",
        "aws-cdk.aws-route53>=1.129.0, <2.0.0",
        "aws-cdk.aws-secretsmanager>=1.129.0, <2.0.0",
        "aws-cdk.aws-sns-subscriptions>=1.129.0, <2.0.0",
        "aws-cdk.aws-sns>=1.129.0, <2.0.0",
        "aws-cdk.aws-ssm>=1.129.0, <2.0.0",
        "aws-cdk.core>=1.129.0, <2.0.0",
        "aws-cdk.cx-api>=1.129.0, <2.0.0",
        "aws-cdk.pipelines>=1.129.0, <2.0.0",
        "constructs>=3.3.161, <4.0.0",
        "jsii>=1.37.0, <2.0.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Typing :: Typed",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
