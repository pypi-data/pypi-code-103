import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-minecraft-server",
    "version": "0.0.2",
    "description": "cdk-minecraft-server",
    "license": "Apache-2.0",
    "url": "https://github.com/Weasledorf-Inc/cdk-minecraft-server",
    "long_description_content_type": "text/markdown",
    "author": "Hasan Abu-Rayyan<hasanaburayyan21@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/Weasledorf-Inc/cdk-minecraft-server"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_minecraft_server",
        "cdk_minecraft_server._jsii"
    ],
    "package_data": {
        "cdk_minecraft_server._jsii": [
            "cdk-minecraft-server@0.0.2.jsii.tgz"
        ],
        "cdk_minecraft_server": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-apigatewayv2-integrations>=1.34.0, <2.0.0",
        "aws-cdk.aws-apigatewayv2>=1.34.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.34.0, <2.0.0",
        "aws-cdk.aws-ecr-assets>=1.34.0, <2.0.0",
        "aws-cdk.aws-ecr>=1.34.0, <2.0.0",
        "aws-cdk.aws-iam>=1.34.0, <2.0.0",
        "aws-cdk.aws-lambda-nodejs>=1.34.0, <2.0.0",
        "aws-cdk.aws-lambda-python>=1.34.0, <2.0.0",
        "aws-cdk.aws-s3-deployment>=1.34.0, <2.0.0",
        "aws-cdk.aws-s3>=1.34.0, <2.0.0",
        "aws-cdk.core>=1.34.0, <2.0.0",
        "cdk-ecr-deployment>=0.0.87, <0.0.88",
        "constructs>=3.2.27, <4.0.0",
        "jsii>=1.46.0, <2.0.0",
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
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
