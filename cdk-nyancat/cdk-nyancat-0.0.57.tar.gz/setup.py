import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-nyancat",
    "version": "0.0.57",
    "description": "cdk-nyancat",
    "license": "Apache-2.0",
    "url": "https://github.com/clarencetw/cdk-nyancat.git",
    "long_description_content_type": "text/markdown",
    "author": "Clarence<me@clarence.tw>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/clarencetw/cdk-nyancat.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_nyancat",
        "cdk_nyancat._jsii"
    ],
    "package_data": {
        "cdk_nyancat._jsii": [
            "cdk-nyancat@0.0.57.jsii.tgz"
        ],
        "cdk_nyancat": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-ec2>=1.95.2, <2.0.0",
        "aws-cdk.aws-s3-assets>=1.95.2, <2.0.0",
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
