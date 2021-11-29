#!/usr/bin/env python

"""The setup script."""

import pathlib
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


# The directory containing this file
here = pathlib.Path(__file__).parent.absolute()

requirements_file_path = here / "requirements.txt"
with open(requirements_file_path) as fh:
    install_requires = [i for i in fh if not i.startswith(("--", "#"))]

dev_requirements_file_path: pathlib.Path = here / "requirements_dev.txt"
with open(dev_requirements_file_path) as fh:
    dev_requires = [i for i in fh if not i.startswith(("--", "#"))]


setup(
    author="Yordan Bautista",
    author_email='bautyor@chrobinson.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Structure logging for Elastic APM tracing",
    install_requires=install_requires,
    extras_require={"dev": dev_requires},
    license="MIT license",
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='struct logging, elastic',
    name='chr_struct_logging',
    packages=find_packages(include=['chr_struct_logging', 'chr_struct_logging.*']),
    url='https://github.com/yordan-bautista-chr/chr_struct_logging',
    version='0.1.1',
    zip_safe=False,
)
