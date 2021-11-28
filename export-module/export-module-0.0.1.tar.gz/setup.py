'''
Author: 兄弟们Go
Date: 2021-11-07 16:54:43
LastEditTime: 2021-11-28 19:12:10
LastEditors: 兄弟们Go
Description: 
FilePath: \export-module\setup.py

'''
import setuptools
try:
    with open("README.md", "r") as fh:
        long_description = fh.read()
except Exception as e:
    long_description = "A package solving the problem of import function"
setuptools.setup(
    name="export-module",
    version="0.0.1",
    author="xiongdi",
    author_email="xdykj@outlook.com",
    description="A package that implement the import and export method",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/huer512/export-module",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
    ],
    python_requires='>=3.6',
    install_requires=[],
)
