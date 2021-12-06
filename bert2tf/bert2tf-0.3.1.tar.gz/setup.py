import os
import sys

import requests
from setuptools import find_packages, setup

if sys.version_info >= (3, 10, 0) or sys.version_info < (3, 8, 0):
    raise OSError(f'bert2tf requires Python 3.8/3.9, but yours is {sys.version}')

__description__ = 'A framework for user easy to load pre trained models with tensorflow keras, like bert gpt2 etc'
if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        __long_description__ = f.read()
else:
    __long_description__ = __description__

setup(
    name='bert2tf',
    version=requests.get('https://api.github.com/repos/xiongma/bert2tf/releases/latest').json()['tag_name'][1:],
    description=(__description__,),
    long_description=__long_description__,
    long_description_content_type='text/markdown',
    author='Xiong Ma',
    author_email='cally.maxiong@gmail.com',
    maintainer='Xiong Ma',
    maintainer_email='cally.maxiong@gmail.com',
    license='Apache 2.1',
    packages=find_packages(),
    include_package_data=True,
    platforms=['linux', 'mac'],
    url='https://github.com/xiongma/bert2tf',
    download_url='https://github.com/xiongma/bert2tf/tags',
    install_requires=[pkg for pkg in open('requirements.txt').read().strip().split('\n')],
    python_requires='>=3.8.0'
)
