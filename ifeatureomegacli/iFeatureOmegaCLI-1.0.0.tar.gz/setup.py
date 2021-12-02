#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Zhen Chen(chenzhen-win2009@163.com; zhenchen625@hotmail.com)
# Description: iFeatureOmega is an integrative platform for the prediction/feature engineering, visualization and analysis of features from molecular sequence, structural and ligand data sets.

from setuptools import setup, find_packages

setup(
    name = 'iFeatureOmegaCLI',
    version = '1.0.0',
    keywords='iFeatureOmegaCLI',
    description = 'An integrative platform for the prediction/feature engineering, visualization and analysis of features from molecular sequence, structural and ligand data sets',
    license = 'MIT License',
    url = 'https://github.com/Superzchen/iFeatureOmega-CLI',
    author = 'SuperZhen',
    author_email = 'chenzhen-win2009@163.com',    
    packages=find_packages("src"),
    package_dir = {'':'src'},
    
    package_data = {
        # 任何包中含有.txt文件，都包含它
        '': ['*.txt'],
        # 包含demo包data文件夹中的 *.dat文件
        'iFeatureOmegaCLI': ['data/*.txt', 'data/*.data', 'data_examples/*.csv', 'data_examples/*.txt', 'data_examples/*.pdb', 'parameters/*.json'],
    },
    platforms = 'any',
    install_requires = [
        'networkx',        
        'numpy>=1.21.4',
        'pandas>=1.3.4',        
        'scikit-learn>=1.0.1',
        'scipy>=1.7.3',
        'matplotlib>=3.5.0'
        ],     
)