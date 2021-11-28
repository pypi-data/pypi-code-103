#!/usr/bin/python
#   resultsFile is a library which allows to read output files of quantum 
#   chemistry codes and write input files.
#   Copyright (C) 2007 Anthony SCEMAMA 
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#   Anthony Scemama
#   LCPQ - IRSAMC        
#   Universite Paul Sabatier
#   118, route de Narbonne      
#   31062 Toulouse Cedex 4      
#   scemama@irsamc.ups-tlse.fr 

import sys                                                                                    

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name="resultsFile",
  version='2.2',
  author="Anthony Scemama",
  author_email="scemama@irsamc.ups-tlse.fr",
  description="Module for reading output files of quantum chemistry codes.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://gitlab.com/scemama/resultsFile",
  download_url="https://gitlab.com/scemama/resultsFile/-/archive/v2.2/resultsFile-v2.2.tar.gz",
  packages=setuptools.find_packages(),
  classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
         "Operating System :: POSIX :: Linux",
     ],
  keywords = ['quantum chemistry', 'GAMESS', 'Gaussian' ],
 )                                                        

