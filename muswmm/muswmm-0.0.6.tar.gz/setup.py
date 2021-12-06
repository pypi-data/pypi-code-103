# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 14:12:41 2021

@author: mumuz
"""

import setuptools

setuptools.setup(name='muswmm',
                 version='0.0.6',
                 description='Muswmm is a library that allows users to modify SWMM project, run SWMM simulation, and get output results.',
                 url='',
                 author='Lei Zhang',
                 author_email='gemini.zhang@qq.com',
                 license='MIT',
                 packages=setuptools.find_packages(),
				 package_data={'':['*.dll'],})