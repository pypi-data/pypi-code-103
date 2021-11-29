# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.md", encoding='utf-8').read()
except IOError:
    long_description = ""

setup(
    name="qrunner",
    version="0.4.7",
    description="UI自动化测试框架",
    author="杨康",
    author_email="772840356@qq.com",
    url="https://github.com/bluepang/qrunner",
    platforms="Android,IOS",
    packages=find_packages(),
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
    package_data={
        r'': ['*.ini'],
    },
    install_requires=['tidevice==0.5.3', 'facebook-wda==1.4.3', 'uiautomator2==2.16.10', 'selenium==4.0.0',
                      'pytest==6.2.5', 'pytest-html==3.1.1', 'pytest-rerunfailures==10.2', 'allure-pytest==2.9.45',
                      'pandas==1.3.4', 'openpyxl==3.0.9', 'XlsxWriter==3.0.2'],
    entry_points={
        'console_scripts': [
            'qrun = qrunner.cli:main'
        ]
    },
)
