#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages



setup(
    name = 'DLWrap',         # How you named your package folder (foo)
    packages = ['DLWrap'],   # Chose the same as "name"
    version = '2.0',      # Start with a small number and increase it with every change you make
    license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description = 'Convert web cookies to dictionary',   # Give a short description about your library
    #long_description=open('README.rst').read(),
    author = 'Yalu Wen',                   # Type in your name
    author_email = 'y.wen@auckland.ac.nz',      # Type in your E-Mail
    #packages=find_packages(),
    platforms=["all"],
    url = 'https://github.com/Yiguan/Cookie2Dict/',   # Provide either the link to your github or to your website
    download_url = 'https://github.com/Yiguan/Cookie2Dict/archive/master.zip',
    keywords = ['Deep learning', 'feature selection', 'Prediction'],   # Keywords that define your package best
    install_requires=['tensorflow','sklearn','numpy','argparse','pandas','keras','statistics'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)