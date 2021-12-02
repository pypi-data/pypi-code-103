# -*- coding: UTF-8 -*-
import os
 
import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='road_detect',
    version='0.0.1',
    keywords='detect',
    description='A demo for road detect.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    package_data={'detect_package':['model-encrypted','road-encrypted']},
    author='zhang1992wen1023',      
    author_email='591603256@qq.com',  
    packages=setuptools.find_packages(),
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[               
        'Crypto==3.11.0',
        'flask==1.1.2',
        'numpy==1.18.5',
        'pandas==1.0.5',
        'xgboost==1.4.2',
        'shap==0.40.0',
    ],
)
