from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "Readme.md").read_text()

setup(
    name='FileManagerPro',
    version='1.0.1',
    description='A Python package with extensive file managing capabilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/arpansahu/FileManagerPro',
    author='Arpan Sahu',
    author_email='arpanrocks95@gmail.com',
    license='BSD 2-clause',
    packages=['FileManagerPro'],
    install_requires=[
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)