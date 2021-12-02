import setuptools

setuptools.setup(
    name="aws-secrets-manager",
    version="0.0.1",
    author="id0",
    description="Helper for AWS Secrets Manager",
    license='MIT',
    packages=["aws_secrets_manager"],
    python_requires='>=3.7',
    install_requires=[
        'boto3'
    ]
)
