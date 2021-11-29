import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-simple-serverless",
    "version": "0.0.26",
    "description": "CDK Constructs for Serverless Demo",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdk-simple-serverless.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<pahudnet@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdk-simple-serverless.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_simple_serverless",
        "cdk_simple_serverless._jsii"
    ],
    "package_data": {
        "cdk_simple_serverless._jsii": [
            "cdk-simple-serverless@0.0.26.jsii.tgz"
        ],
        "cdk_simple_serverless": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-apigateway>=1.95.2, <2.0.0",
        "aws-cdk.aws-lambda>=1.95.2, <2.0.0",
        "aws-cdk.core>=1.95.2, <2.0.0",
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
