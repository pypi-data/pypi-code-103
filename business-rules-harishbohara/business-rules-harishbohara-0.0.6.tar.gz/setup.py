#! /usr/bin/env python

import setuptools

with open('HISTORY.rst') as f:
    history = f.read()

description = 'Python DSL for setting up business intelligence rules that can be configured without code'

setuptools.setup(
    name='business-rules-harishbohara',
    version="0.0.6",
    description='{0}\n\n{1}'.format(description, history),
    author='Harish Bohara',
    author_email='harish.bohara@gmail.com',
    url='https://github.com/harishb2k/business-rules',
    packages=['business_rules'],
    package_dir={"": "."},
    license='MIT'
)
