import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "superluminar-io.super-eks",
    "version": "0.2.10",
    "description": "super-eks is a CDK construct that provides a preconfigured EKS installation with batteries included.",
    "license": "Apache-2.0",
    "url": "https://github.com/superluminar-io/super-eks.git",
    "long_description_content_type": "text/markdown",
    "author": "superluminar",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/superluminar-io/super-eks.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "superluminar_io.super_eks",
        "superluminar_io.super_eks._jsii"
    ],
    "package_data": {
        "superluminar_io.super_eks._jsii": [
            "super-eks@0.2.10.jsii.tgz"
        ],
        "superluminar_io.super_eks": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-ec2>=1.134.0, <2.0.0",
        "aws-cdk.aws-eks>=1.134.0, <2.0.0",
        "aws-cdk.aws-iam>=1.134.0, <2.0.0",
        "aws-cdk.aws-route53>=1.134.0, <2.0.0",
        "aws-cdk.core>=1.134.0, <2.0.0",
        "aws-cdk.custom-resources>=1.134.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
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
