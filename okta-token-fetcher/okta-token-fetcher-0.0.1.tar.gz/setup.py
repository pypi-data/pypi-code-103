
#!/usr/bin/env python3.8
from setuptools import setup, find_packages


install_requires = [
    "requests",
    "pyjwt"
]

description = "Used to fetch OKTA tokens for an application using web a browser that redirects to a commandline server"

setup(
    name="okta-token-fetcher",
    version="0.0.1",
    description=description,
    long_description=description,
    author="Mathew Moon",
    author_email="me@mathewmoon.net",
    # Choose your license
    python_requires=">=3.8",
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
    #package_dir={
    #    "okta_token_fetcher": "okta_token_fetcher"
    #},
    #include_package_data=True,
    entry_points = {
      "console_scripts": [
        "okta-fetch = okta_token_fetcher:run_from_shell"
      ]
    },
    packages=["okta_token_fetcher"]
)
