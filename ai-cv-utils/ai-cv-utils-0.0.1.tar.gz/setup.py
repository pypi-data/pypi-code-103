# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

install_requires=[
    'cycler',
    'kiwisolver',
    'matplotlib',
    'numpy',
    'opencv-python-headless',
    'Pillow',
    'pyparsing',
    'python-dateutil',
    'six',
    'click',
]

setup(
    name='ai-cv-utils',
    version='0.0.1',
    author='Gaston Alberto Bertolani',
    author_email='gbertolani.in@gmail.com',
    description='AI Computer Vision Utilities',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/gbertolani/ai-cv-utils',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Utilities',

    ],
    license='AGPL3+',
    packages=find_packages(),
    python_requires='>=3.6',
    entry_points='''
        [console_scripts]
        aicv=aicv.main:aicv
    ''',

)
