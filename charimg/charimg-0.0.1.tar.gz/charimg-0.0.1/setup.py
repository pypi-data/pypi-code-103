#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='charimg',
    version='0.0.1',
    description="a tiny tool to print image in cmdline",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/insorker/charimg-py",
    author='insorker',
    author_email='insorker@qq.com',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    keywords='python image char',
    license='MIT',
    package_dir={'': 'src'},
    packages = find_packages(where='src'),
    python_requires=">=3.6",
    install_requires=[
        'Pillow',
    ],
)
