
#!/usr/bin/env python3.8
from setuptools import setup, find_packages


install_requires = [
    "requests",
    "pyjwt"
]

description = "Used to fetch OKTA tokens for an application using web a browser that redirects to a commandline server"
with open("README.md", "r") as f:
  long_description = f.read()

setup(
    name="okta-token-fetcher",
    version="0.0.3",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mathew Moon",
    author_email="me@mathewmoon.net",
    # Choose your license
    python_requires=">=3.8",
    url="https://github.com/mathewmoon/okta-token-fetcher",
    license="Apache 2.0",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
        x for x in install_requires if x not in ["boto3", "botocore"]
    ],
    entry_points = {
      "console_scripts": [
        "okta-fetch = okta_token_fetcher:run_from_shell"
      ]
    },
    packages=["okta_token_fetcher"]
)
