import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "ikala-cloud.aws-waf-solution",
    "version": "1.0.31",
    "description": "Cloudfront,ALB and API Gateway with Automated WAF",
    "license": "Apache-2.0",
    "url": "https://github.com/iKala-Cloud/aws-waf-solution",
    "long_description_content_type": "text/markdown",
    "author": "Chris Yang",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/iKala-Cloud/aws-waf-solution"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "ikala-cloud.aws-waf-solution",
        "ikala-cloud.aws-waf-solution._jsii"
    ],
    "package_data": {
        "ikala-cloud.aws-waf-solution._jsii": [
            "aws-waf-solution@1.0.31.jsii.tgz"
        ],
        "ikala-cloud.aws-waf-solution": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-apigateway>=1.123.0, <2.0.0",
        "aws-cdk.aws-athena>=1.123.0, <2.0.0",
        "aws-cdk.aws-cloudfront>=1.123.0, <2.0.0",
        "aws-cdk.aws-cloudwatch>=1.123.0, <2.0.0",
        "aws-cdk.aws-events-targets>=1.123.0, <2.0.0",
        "aws-cdk.aws-events>=1.123.0, <2.0.0",
        "aws-cdk.aws-glue>=1.123.0, <2.0.0",
        "aws-cdk.aws-iam>=1.123.0, <2.0.0",
        "aws-cdk.aws-kinesisfirehose>=1.123.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.123.0, <2.0.0",
        "aws-cdk.aws-s3-notifications>=1.123.0, <2.0.0",
        "aws-cdk.aws-s3>=1.123.0, <2.0.0",
        "aws-cdk.aws-wafv2>=1.123.0, <2.0.0",
        "aws-cdk.core>=1.123.0, <2.0.0",
        "aws-cdk.custom-resources>=1.123.0, <2.0.0",
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
