#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2019  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gmail.com>
# Maintainer: David Arroyo Menéndez <davidam@gmail.com>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with DameFaces; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

import os
from setuptools import setup
from os import path

# def readme():
#     with open('README.org') as f:
#         return f.read()

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

cwd = os.getcwd()

def files_one_level(directory):
    f = os.popen('find '+ directory )
    l = []
    for line in f:
        fields = line.strip().split()
        l.append(fields[0])
    return l

def files_one_level_drop_pwd(directory):
    f = os.popen('find '+ directory)
    l = []
    for line in f:
        fields = line.strip().split()
        if not(os.path.isdir(fields[0])) and ("__init__.py" not in fields[0]):
            l.append(drop_pwd(fields[0]))
    return l

def drop_pwd(s):
    cwd = os.getcwd()
    result = ""
    if re.search(cwd, s):
        result = re.sub(cwd+'/', '', s)
    return result

    
setup(name='damefaces',
      version='0.0.2.post9',
      description='Learning Faces from Tests by David Arroyo Menéndez',
      long_description=long_description,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
      ],
      keywords='faces tests',
      scripts=['damefaces/bin/damefaces.py'],
      url='http://github.com/davidam/damefaces',
      author='David Arroyo Menéndez',
      author_email='davidam@gmail.com',
      license='GPLv3',
      packages=['damefaces', 'damefaces.bin'],
      package_dir={'damefaces': 'damefaces',
                   'damefaces.files': 'damefaces.files',                   
                   'damefaces.bin': 'damefaces/bin'},
      package_data={'damefaces': ['*'],
                    'damefaces.files': ['*'],                    
                    'damefaces.bin': ['*']},      
      data_files=[('damefaces', ['damefaces/bin/age_net.caffemodel', 'damefaces/bin/opencv_face_detector.pbtxt', 'damefaces/bin/opencv_face_detector_uint8.pb', 'damefaces/bin/gender_deploy.prototxt', 'damefaces/bin/age_deploy.prototxt', 'damefaces/bin/gender_net.caffemodel', 'damefaces/files/kid1.jpg', 'damefaces/files/kid2.jpg', 'damefaces/files/girl1.jpg', 'damefaces/files/girl2.jpg', 'damefaces/files/man1.jpg', 'damefaces/files/man2.jpg'])],
      install_requires=[
          'markdown',
          'opencv-python',
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      include_package_data=True,
      zip_safe=False)
