# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 14:12:41 2021

@author: mumuz
"""

import setuptools

setuptools.setup(name='simuwater',
                 version='0.0.6',
                 description='Simuwater is a control-oriented modelling software',
                 url='',
                 author='Lei Zhang',
                 author_email='gemini.zhang@qq.com',
                 license='MIT',
                 packages=setuptools.find_packages(),
				 package_data={'':['*.dll'],})