#!/usr/bin/env python

import re
import setuptools

version = ""
with open('xdj_utils/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xdj-utils",
    version=version,
    author="18580543261",
    author_email="595127207@qq.com",
    description="a util set for django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT Licence",
    url="https://gitee.com/xdjango/xdj_utils.git",
    install_requires=[
        "asgiref==3.3.4",
        "Django==3.2.3",
        "django-filter==2.4.0",
        "djangorestframework==3.12.4",
        "djangorestframework_simplejwt==4.7.1",
        "pytz==2021.1",
        "six==1.16.0",
        "user-agents==2.2.0",
        "drf-yasg==1.20.0",
        "gitpython==3.1.20",
        "whitenoise==5.3.0",
    ],
    packages=setuptools.find_packages(),
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ),
    exclude_package_data={'': ["requirements.txt"]},
)
