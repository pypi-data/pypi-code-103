from os.path import dirname, abspath, join
from setuptools import setup

NAME: str = "withv2"
AUTHOR: str = "Saadman Rafat"
DESCRIPTION: str = "CLI to interact with Twitter"
URL: str = "https://github.com/twitivity/withv2"
REQUIRES_PYTHON: str = ">=3.6.0"
VERSION = "0.2.1-alpha"
REQUIRED = [
    "requests==2.25.0",
    "requests-oauthlib==1.3.0",
    "PyYAML==5.4.1",
    "prompt-toolkit",
    "sshuttle",
]
EMAIL = "saadmanhere@gmail.com"

with open(join(abspath(dirname(__file__)), "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name=NAME,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    license="MIT",
    install_requires=REQUIRED,
    py_modules=["withv2"],
    entry_points={"console_scripts": "withv2=withv2:cli"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Unix",
    ],
    keywords="CLI Tool for Twitter API V2",
    tests_require=["pytest"],
)
