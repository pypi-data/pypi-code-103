"""Setup the python module."""

import os
from setuptools import setup, find_packages  # type: ignore

with open(
    "README.md",
    "r",
    encoding="utf-8",
) as fh:
    long_description = fh.read()

with open(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "redbrick_sagemaker",
        "VERSION",
    ),
    "r",
    encoding="utf-8",
) as f:
    version = f.read().strip()

install_requires = [
    "redbrick-sdk>=0.6.13",
    "sagemaker==2.60.0",
    "boto3==1.20.11",
    "mxnet>=1.5.0",
    "opencv-python==4.5.4.60",
]

setup(
    name="redbrick_sagemaker",
    url="https://github.com/redbrick-ai/redbrick-sagemaker",
    version=version,
    description="RedBrick AI and AWS Sagemaker integration",
    py_modules=["redbrick-sagemaker"],
    python_requires=">=3.7.0, <3.10",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        "dev": [
            "wheel==0.35.1",
            "pytest-mock==3.3.1",
            "pytest==6.1.2",
            "black==21.7b0",
            "mypy==0.790",
            "mypy-extensions==0.4.3",
            "pylint==2.11.1",
            "pycodestyle==2.6.0",
            "pydocstyle==5.1.1",
            "flake8==3.8.4",
            "flake8-print==3.1.4",
            "eradicate==1.0",
            "pytest-cov>=2.8.1",
            "pytest-asyncio==0.12.0",
            "pytest-eradicate==0.0.5",
            "pytest-pycodestyle==2.2.0",
            "pytest-pydocstyle==2.2.0",
            "pytest-black==0.3.12",
            "pytest-pylint==0.17.0",
            "pytest-mypy==0.7.0",
            "pytest-flake8==1.0.6",
            "pytest-randomly==3.4.1",
        ]
    },
)
