import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "crow-api.core",
    "version": "1.0.1",
    "description": "AWS CDK Construct to create a serverless API based on file structure.",
    "license": "Apache-2.0",
    "url": "https://github.com/thomasstep/crow-api",
    "long_description_content_type": "text/markdown",
    "author": "Thomas Step<thomas@thomasstep.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/thomasstep/crow-api.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "crow_api.core",
        "crow_api.core._jsii"
    ],
    "package_data": {
        "crow_api.core._jsii": [
            "crow-api@1.0.1.jsii.tgz"
        ],
        "crow_api.core": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk-lib==2.0.0",
        "constructs>=10.0.9, <11.0.0",
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
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": [
        "src/crow_api/core/_jsii/bin/crow-api"
    ]
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
