# -*- coding: utf-8 -*-
import sys

from setuptools import setup
import simplepro

if sys.version_info < (3, 0):

    long_description = "\n".join([
        open('README.rst', 'r').read(),
    ])
else:
    long_description = "\n".join([
        open('README.rst', 'r', encoding='utf-8').read(),
    ])

# 如果是Windows，就安装wmi和pywin32模块


requires = ['django>=2.1', 'django-simpleui>=2021.11.5', 'django-import-export', 'requests', 'rsa', 'psutil']

# if sys.platform == 'win32':
#     requires.append('pywin32')
#     requires.append('wmi')

setup(
    name='simplepro',
    version=simplepro.get_version(),
    packages=['simplepro'],
    zip_safe=False,
    include_package_data=True,
    url='https://github.com/newpanjing/simpleui',
    license='Apache License 2.0',
    author='panjing',
    long_description=long_description,
    author_email='newpanjing@icloud.com',
    description='django admin theme 后台模板',
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
