#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @CreateDate   : 21/11/26 17:35
# @Author       : DBArtist
# @Email        : 1595628527@qq.com
# @ScriptFile   : setup.py
# @Project      : PyMonitor
# @Describe     :

# from setuptools import setup, find_packages
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# with open('requirements.txt', "r", encoding="utf-8") as f:
#    requires = f.read().splitlines()


setuptools.setup(
    name="dbartist",
    version="0.0.7",
    author="dbartist",
    author_email="1595628527@qq.com",
    description="description",
    long_description="###dbartist long description.",
    long_description_content_type="text/markdown",
    url="https://github.com/DBArtist",
    license="GPLv3",
    packages=setuptools.find_packages(),
    py_modules=["dbartist"],
    # package_dir={"":"src"},
    install_requires = [
        "Click",
        "requests",
    ],
   entry_points = {
        "console_scripts": [
        'robot = src.robot:main'
        ]
    },
    # include_package_data=True,
    # zip_safe=True,
    # exclude_package_data={'': ['__pycache__']},
    # download_url = "",
    keywords=["dbartist"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],

)